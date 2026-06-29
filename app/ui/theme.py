# ui/theme.py

import re
from pathlib import Path
import streamlit as st

def apply_theme():
    css = Path(__file__).parent.joinpath("styles.css").read_text()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    
def get_theme_colors():
    """Parses color variables defined in styles.css and returns them as a dict."""
    css_path = Path(__file__).parent.joinpath("styles.css")
    if not css_path.exists():
        return {}
    css = css_path.read_text(encoding="utf-8")
    # Match --var-name: value;
    matches = re.findall(r"--([\w-]+):\s*([^;]+);", css)
    return {name.upper().replace("-", "_"): value.strip() for name, value in matches}