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
        "lumanSense", "app/ui/assets/favicon_small.png", "Real-time lighting intelligence overview"
    )

    theme.apply_theme("base.css", "agent.css")
    st.markdown('<div id="link-to-top"></div>', unsafe_allow_html=True)

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
    col_title, col_status = st.columns([4, 1])
    with col_title:
        typography.render_page_header("Ask LumanSense", "Smart Lighting Assistant")
    with col_status:
        if agent_online:
            st.markdown(
                '<div style="text-align:right; margin-top: 24px;">'
                '<span class="status-badge status-online">'
                '<span class="status-dot"></span> Agent Online</span></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div style="text-align:right; margin-top: 24px;">'
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

    # Page layout split side-by-side
    col_left, col_right = st.columns([1.1, 2.9], gap="large")

    # ── LEFT PANEL: Suggested/Default Questions ─────────────────────────────
    with col_left:
        with st.container(key="ai_left_panel"):
            st.markdown(
                '<div class="luman-panel-title" style="margin-bottom: 6px;">💬 Suggested question</div>',
                unsafe_allow_html=True,
            )
            suggested_query = render_suggested_queries()

    # ── RIGHT PANEL: Conversation ───────────────────────────────────────────
    with col_right:
        with st.container(key="ai_right_panel"):
            st.markdown('<div class="gemini-gradient-header">Conversation with LumanSense AI</div>', unsafe_allow_html=True)
            st.markdown('<div style="margin-bottom: 20px;"></div>', unsafe_allow_html=True)

            # Chat Input Box at the top of the conversation panel
            chat_query = st.chat_input("Ask LumanSense AI...")
            if chat_query:
                suggested_query = chat_query

            if not st.session_state.ai_history and not suggested_query:
                st.markdown(
                    '<div style="text-align:center; padding: 40px 20px; '
                    'color: var(--text-secondary, #6b7094); font-size: 14px;">'
                    "No messages yet — choose a suggested prompt on the left or type your query above to get started.</div>",
                    unsafe_allow_html=True,
                )

            # Render temporary question and pulsing Gemini loader dots while agent is processing (at the top)
            if suggested_query:
                with st.chat_message("user", avatar="🧑"):
                    st.write(suggested_query)
                with st.chat_message("assistant", avatar="💡"):
                    st.markdown(
                        """
                        <div class="gemini-loader">
                            <span class="dot"></span>
                            <span class="dot"></span>
                            <span class="dot"></span>
                        </div>
                        <style>
                        .gemini-loader {
                            display: flex;
                            align-items: center;
                            gap: 6px;
                            padding: 8px 0;
                        }
                        .gemini-loader .dot {
                            width: 8px;
                            height: 8px;
                            border-radius: 50%;
                            background: linear-gradient(90deg, #4285f4, #9b72cb, #ff52da);
                            animation: geminiPulse 1.2s infinite ease-in-out;
                            display: inline-block;
                        }
                        .gemini-loader .dot:nth-child(2) {
                            animation-delay: 0.2s;
                        }
                        .gemini-loader .dot:nth-child(3) {
                            animation-delay: 0.4s;
                        }
                        @keyframes geminiPulse {
                            0%, 100% {
                                transform: scale(0.6);
                                opacity: 0.4;
                            }
                            50% {
                                transform: scale(1.2);
                                opacity: 1;
                            }
                        }
                        </style>
                        """,
                        unsafe_allow_html=True,
                    )

            # Render history in reverse order (newest at the top)
            for entry in reversed(st.session_state.ai_history):
                with st.chat_message("user", avatar="🧑"):
                    st.write(entry["q"])
                with st.chat_message("assistant", avatar="💡"):
                    st.markdown(
                        f'<div style="color:#c0c4d6; font-size:16px; line-height:1.6;">{entry["a"]}</div>',
                        unsafe_allow_html=True,
                    )
                    if entry.get("latency") is not None:
                        st.markdown(
                            f'<div class="latency-tag">⏱ answered in {entry["latency"]:.2f}s</div>',
                            unsafe_allow_html=True,
                        )

    # ── Input + agent call ─────────────────────────────────────────────────────────
    if suggested_query:
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
            response_text = _run_async(get_response(suggested_query, _runner))
            elapsed = time.time() - start

            st.session_state.ai_history.append(
                {"q": suggested_query, "a": response_text, "latency": elapsed}
            )
            st.rerun()
        except Exception as e:
            st.error(f"Error communicating with lumanSense: {e}")


def render_suggested_queries():
    suggestions = [
        {
            "icon": "⚡",
            "text": "Calculate total energy savings and CO2 reduction",
        },
        {
            "icon": "🚶",
            "text": "Analyze average pedestrian count and peak traffic per zone",
        },
        {
            "icon": "🕵️",
            "text": "Audit recent dimming decisions for safety overrides",
        },
        {
            "icon": "🔮",
            "text": "Predict the pedestrian flow distribution after 3 steps for Zone A",
        },
        {
            "icon": "📋",
            "text": "List the last 5 dimming decisions with justifications",
        },
    ]

    suggested_query = None
    with st.container(key="suggested_queries_vertical"):
        for idx, s in enumerate(suggestions):
            if st.button(
                f"{s['icon']} {s['text']}",
                key=f"sug_vert_{idx}",
                use_container_width=True,
            ):
                suggested_query = s["text"]

    return suggested_query
