import streamlit as st


def configure_page(title, icon, subtitle=None):
    try:
        st.set_page_config(
            page_title=title,
            page_icon=icon,
            layout="wide",
            initial_sidebar_state="expanded",
        )
    except Exception:
        pass


def render_page_header(title, subtitle):
    st.markdown(
        f"""
    <div class="page-header">
        <span class="page-title">{title}</span>
        <span class="page-subtitle">{subtitle}</span>
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_section_header(title):
    with st.container():
        st.markdown(
            f"""
        <div class="section-header">
            <span>{title}</span>
        </div>
        """,
            unsafe_allow_html=True,
        )
