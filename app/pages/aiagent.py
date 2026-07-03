import os
import sys

from app.ui import theme, typography

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if project_root not in sys.path:
    sys.path.append(project_root)

import asyncio  # noqa: E402
import threading  # noqa: E402
import time  # noqa: E402

import streamlit as st  # noqa: E402

try:
    from dotenv import load_dotenv
    from google.adk.runners import App, Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types

    from app.agent.ask_luman_agent import ask_luman_agent
except ImportError as e:
    st.error("Missing dependencies.\n\nRun:\nuv run streamlit run app/dashboard.py")
    st.exception(e)
    st.stop()

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("GEMINI_API_KEY not found in environment.")
    st.stop()


# ── Async helper ───────────────────────────────────────────────────────────────
def _run_async(coro):
    """Run an async coroutine in a fresh thread+event loop — safe inside Streamlit."""
    result_holder, exc_holder = {}, {}

    def _target():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result_holder["v"] = loop.run_until_complete(coro)
        except Exception as exc:
            exc_holder["e"] = exc
        finally:
            loop.close()

    t = threading.Thread(target=_target)
    t.start()
    t.join()
    if "e" in exc_holder:
        raise exc_holder["e"]
    return result_holder.get("v")


def render_ai_agent():
    typography.configure_page(
        "lumanSense", "💡", "Real-time lighting intelligence overview"
    )

    theme.apply_theme("base.css", "agent.css")

    if "runner" not in st.session_state:
        try:
            _app = App(name="ask_luman_app", root_agent=ask_luman_agent)
            _svc = InMemorySessionService()

            # FIX: create_session is async — use the built-in sync variant.
            # Previous code called create_session() without await, which returned
            # a coroutine object and never actually created the session, causing
            # "Session not found: chat_session" on every run_async call.
            _svc.create_session_sync(
                app_name="ask_luman_app", user_id="user", session_id="chat_session"
            )

            st.session_state.session_service = _svc
            st.session_state.runner = Runner(app=_app, session_service=_svc)
            st.session_state.runner_error = None
        except Exception as e:
            st.session_state.runner = None
            st.session_state.runner_error = str(e)

    if "ai_history" not in st.session_state:
        st.session_state.ai_history = []

    agent_online = st.session_state.runner is not None

    # ── Header row: title + live status badge ───────────────────────────────────────
    typography.render_page_header("Ask LumanSense", "Smart Lighting Assistant")

    _header_col, status_col = st.columns([4, 1])
    with status_col:
        if agent_online:
            st.markdown(
                '<div style="text-align:right;">'
                '<span class="status-badge status-online">'
                '<span class="status-dot"></span> Agent Online</span></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div style="text-align:right;">'
                '<span class="status-badge status-offline">'
                '<span class="status-dot"></span> Agent Offline</span></div>',
                unsafe_allow_html=True,
            )

    if not agent_online:
        st.error(
            f"Failed to initialise lumanSense agent: {st.session_state.runner_error}"
        )
        st.stop()

    # Capture runner in a local variable — never access st.session_state from
    # inside the background thread; Streamlit's session state is not thread-safe.
    _runner = st.session_state.runner

    # ── Suggested questions panel ────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="luman-panel">
            <div class="luman-panel-title">💬 Quick Questions</div>
        """,
        unsafe_allow_html=True,
    )
    suggested_query = render_suggested_queries()

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Conversation panel ───────────────────────────────────────────────────────────
    header_left, header_right = st.columns([4, 1])
    with header_left:
        typography.render_section_header("Conversation")
    with header_right:
        if st.session_state.ai_history:
            if st.button("🗑 Clear chat", key="clear_chat"):
                st.session_state.ai_history = []
                st.rerun()

    if not st.session_state.ai_history:
        st.markdown(
            '<div class="luman-panel" style="text-align:center; '
            'color: var(--text-secondary, #6b7094); font-size: 13px;">'
            "No messages yet — ask a question above or type below to get started.</div>",
            unsafe_allow_html=True,
        )

    for entry in st.session_state.ai_history:
        with st.chat_message("user", avatar="🧑"):
            st.write(entry["q"])
        with st.chat_message("assistant", avatar="💡"):
            st.markdown(
                f'<div style="color:#F0F0F0; font-size:16px; line-height:1.5;">{entry["a"]}</div>',
                unsafe_allow_html=True,
            )

            if entry.get("latency") is not None:
                st.markdown(
                    f'<div class="latency-tag">⏱ answered in {entry["latency"]:.2f}s</div>',
                    unsafe_allow_html=True,
                )

    # ── Input + agent call ─────────────────────────────────────────────────────────
    user_input = st.chat_input("Ask a question about your energy data...")
    query = suggested_query or user_input

    if query:
        with st.chat_message("user", avatar="🧑"):
            st.write(query)

        with st.chat_message("assistant", avatar="💡"):
            with st.spinner("lumanSense is analyzing your data..."):
                try:

                    async def get_response(prompt: str, runner: Runner) -> str:
                        response_text = ""
                        async for event in runner.run_async(
                            user_id="user",
                            session_id="chat_session",
                            new_message=types.Content(
                                role="user",
                                parts=[types.Part.from_text(text=prompt)],
                            ),
                        ):
                            if event.content and event.content.parts:
                                text = event.content.parts[0].text
                                if text:
                                    response_text += text
                        return response_text

                    start = time.time()
                    response_text = _run_async(get_response(query, _runner))
                    elapsed = time.time() - start

                    st.session_state.ai_history.append(
                        {"q": query, "a": response_text, "latency": elapsed}
                    )
                    st.rerun()
                except Exception as e:
                    st.error(f"Error communicating with lumanSense: {e}")


def render_suggested_queries():
    suggestions = [
        {"icon": "⚡", "text": "What is the total energy saved?"},
        {"icon": "📍", "text": "Which zone is the most active?"},
        {"icon": "🎯", "text": "Give me the latest detection event metrics"},
        {
            "icon": "🔮",
            "text": "Predict the state distribution after 3 steps for Zone A",
        },
        {"icon": "🕵️", "text": "Audit recent decisions"},
    ]

    suggested_query = None
    with st.container(key="suggested_queries"):
        cols = st.columns(len(suggestions), gap="small")
        for idx, s in enumerate(suggestions):
            with cols[idx]:
                if st.button(
                    f"{s['icon']}\n\n{s['text']}",
                    key=f"sug_{idx}",
                    use_container_width=True,
                ):
                    suggested_query = s["text"]

    return suggested_query
