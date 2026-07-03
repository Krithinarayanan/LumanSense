"""About page rendering.

This module renders the system documentation and overview by loading the README.md content.
"""

import os

import streamlit as st

from app.ui import theme, typography


def render_about():
    """Renders the About page with README.md preview."""
    typography.configure_page("lumanSense", "", "System Overview & Documentation")
    theme.apply_theme("base.css", "dashboard.css")
    typography.render_page_header("About LumanSense", "System Overview & Documentation")

    # Read README.md from project root
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    readme_path = os.path.join(project_root, "README.md")

    try:
        with open(readme_path, encoding="utf-8") as f:
            readme_content = f.read()
        # Wrap content in a styled container defined in base.css
        st.markdown(
            f'<div class="about-container">\n\n{readme_content}\n\n</div>',
            unsafe_allow_html=True,
        )
    except FileNotFoundError:
        st.error("Documentation file README.md not found.")
