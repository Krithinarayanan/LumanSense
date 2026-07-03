"""lumanSense User Interface entry point.

This script coordinates and renders the Streamlit web dashboard for municipal
operators, providing real-time lighting telemetry and an AI analysis portal.
"""

import streamlit as st

from app.ui import theme
from app.ui.typography import configure_page

# Configure the page first (mandatory for Streamlit)
configure_page("lumanSense", "💡")

from app.pages.about import render_about  # noqa: E402
from app.pages.aiagent import render_ai_agent  # noqa: E402
from app.pages.dashboard import render_dashboard  # noqa: E402
from app.ui.sidebar import render_sidebar  # noqa: E402

# Apply base and sidebar styling
theme.apply_theme("base.css", "sidebar.css")

params = st.query_params

page = params.get("page", "dashboard")
st.session_state.active_page = page
render_sidebar()

if page == "dashboard":
    render_dashboard()
elif page == "aiagent":
    render_ai_agent()
elif page == "about":
    render_about()
