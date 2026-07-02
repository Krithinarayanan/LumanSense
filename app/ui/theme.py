# ui/theme.py

from pathlib import Path

import streamlit as st

import app.ui.design as design

THEME_COLORS = {
    "primary": "#60A5FA",
    "secondary": "#818CF8",
    "success": "#34D399",
    "warning": "#FBBF24",
    "danger": "#F87171",
    "background": "#0F1117",
    "surface": "#181B23",
    "text_primary": "#F8FAFC",
    "text_secondary": "#94A3B8",
    "border": "#2A2F3A",
}


def apply_theme(*files):

    # Generate CSS variables dynamically from THEME_COLORS
    css = ":root {\n"
    for name, value in design.THEME_COLORS.items():
        css += f"    --{name.replace('_', '-')}: {value};\n"
    for name, value in design.THEME_SPACING.items():
        css += f"    --{name.replace('_', '-')}: {value};\n"

    # Specific variables used by the CSS files
    css += "    --bg-page: var(--background);\n"
    css += "    --bg-card: var(--surface);\n"
    css += "    --bg-surface: var(--surface);\n"
    css += "    --shadow-card: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);\n"
    css += "}\n\n"
    css += """
.section-header {
    color: var(--text-primary);
    font-size: 1.2rem;
    font-weight: 700;
    margin-top: 2rem;
    margin-bottom: 1rem;
    padding-bottom: 0.25rem;
    border-bottom: 1px solid var(--border);
    letter-spacing: 0.01em;
}
"""

    styles = Path(__file__).parent / "styles"

    for file in files:
        css += (styles / file).read_text(encoding="utf-8")
        css += "\n"

    st.markdown(
        f"<style>{css}</style>",
        unsafe_allow_html=True,
    )
