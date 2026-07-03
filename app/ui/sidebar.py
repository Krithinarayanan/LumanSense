import streamlit as st


def render_sidebar():
    with st.sidebar:
        dashboard_active = (
            "active" if st.session_state.active_page == "dashboard" else ""
        )
        ai_active = "active" if st.session_state.active_page == "aiagent" else ""
        about_active = "active" if st.session_state.active_page == "about" else ""
        st.html(f"""
            <div class="activity-bar">
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
