import base64
from pathlib import Path
import streamlit as st


def render_sidebar():
    # Load favicon as base64 to embed inline cleanly at the top of the sidebar activity bar
    import sys
    favicon_path = Path(__file__).parent / "assets" / "favicon.png"
    favicon_html = ""
    if favicon_path.exists():
        try:
            with open(favicon_path, "rb") as f:
                b64_data = base64.b64encode(f.read()).decode()
            favicon_html = f"""
            <div class="activity-logo" style="text-align: center; margin-bottom: 24px; padding-top: 8px; flex-shrink: 0;">
                <img src="data:image/png;base64,{b64_data}" style="width: 32px; height: 32px; border-radius: 6px; box-shadow: 0 1px 4px rgba(0,0,0,0.4);"/>
            </div>
            """
        except Exception as e:
            print(f"Error loading favicon in sidebar: {e}", file=sys.stderr)
    else:
        print(f"Favicon path not found: {favicon_path}", file=sys.stderr)

    with st.sidebar:
        dashboard_active = (
            "active" if st.session_state.active_page == "dashboard" else ""
        )
        ai_active = "active" if st.session_state.active_page == "aiagent" else ""
        about_active = "active" if st.session_state.active_page == "about" else ""
        st.html(f"""
            <div class="activity-bar">
                {favicon_html}
                <a href="?page=dashboard">
                    <div class="activity-icon {dashboard_active}">
                        📊
                    </div>
                </a>
                <a href="?page=aiagent">
                    <div class="activity-icon {ai_active}">
                        🤖
                    </div>
                </a>
                <a href="?page=about">
                    <div class="activity-icon {about_active}">
                        &#8505;&#65039;
                    </div>
                </a>
            </div>
            """)
