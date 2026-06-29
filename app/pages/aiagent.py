from app.ui.sidecard import render_sidebar
import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if project_root not in sys.path:
    sys.path.append(project_root)

import asyncio
import threading

import streamlit as st

from app.ui.theme import apply_theme

st.set_page_config(
    page_title="Ask LumenSense",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_theme()


try:
    from google.adk.runners import App, Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types
    from dotenv import load_dotenv
    from app.agent.ask_lumen_agent import ask_lumen_agent
except ImportError as e:
    st.error("Missing dependencies.\n\nRun:\nuv run streamlit run app/dashboard.py")
    st.exception(e)
    st.stop()

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("GEMINI_API_KEY not found in environment.")
    st.stop()

render_sidebar("aiagent")

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

if "runner" not in st.session_state:
    try:
        _app = App(name="ask_lumen_app", root_agent=ask_lumen_agent)
        _svc = InMemorySessionService()

        # FIX: create_session is async — use the built-in sync variant.
        # Previous code called create_session() without await, which returned
        # a coroutine object and never actually created the session, causing
        # "Session not found: chat_session" on every run_async call.
        _svc.create_session_sync(
            app_name="ask_lumen_app", user_id="user", session_id="chat_session"
        )

        st.session_state.session_service = _svc
        st.session_state.runner          = Runner(app=_app, session_service=_svc)
        st.session_state.runner_error    = None
    except Exception as e:
        st.session_state.runner          = None
        st.session_state.runner_error    = str(e)

if st.session_state.runner is None:
    st.error(f"Failed to initialise LumenSense agent: {st.session_state.runner_error}")
    st.stop()

if "ai_history" not in st.session_state:
    st.session_state.ai_history = []

# Capture runner in a local variable — never access st.session_state from
# inside the background thread; Streamlit's session state is not thread-safe.
_runner = st.session_state.runner

# ── Page header ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header-container">
    <span class="page-header-title">Ask LumenSense</span>
    <span class="page-header-subtitle">AI Analyst & Smart Lighting Assistant</span>
</div>
""", unsafe_allow_html=True)

# ── Suggested questions ────────────────────────────────────────────────────────
st.markdown(
    '<span class="suggested-questions-label">Suggested Questions</span>',
    unsafe_allow_html=True,
)
suggestions = [
    "What is the total energy saved?",
    "Which zone is the most active?",
    "Give me the latest detection event metrics",
    "Predict the state distribution after 3 steps for Zone A",
    "Audit recent decisions",
]

suggested_query = None
cols = st.columns(len(suggestions))
for idx, s in enumerate(suggestions):
    if cols[idx].button(s, key=f"sug_{idx}"):
        suggested_query = s

# ── Chat history ───────────────────────────────────────────────────────────────
for entry in st.session_state.ai_history:
    with st.chat_message("user"):
        st.write(entry["q"])
    with st.chat_message("assistant"):
        st.write(entry["a"])

# ── Input + agent call ─────────────────────────────────────────────────────────
user_input = st.chat_input("Ask a question about your energy data...")
query = suggested_query or user_input

if query:
    with st.chat_message("user"):
        st.write(query)

    with st.spinner("LumenSense is thinking..."):
        try:
            # FIX: use local _runner — never read st.session_state inside
            # the background thread; session state is not thread-safe in Streamlit.
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

            ans = _run_async(get_response(query, _runner))

            st.session_state.ai_history.append({"q": query, "a": ans})

            with st.chat_message("assistant"):
                st.write(ans)

            if suggested_query:
                st.rerun()

        except Exception as e:
            st.error(f"Error communicating with LumenSense: {e}")