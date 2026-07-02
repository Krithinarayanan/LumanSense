import streamlit as st


class PanelContainer:
    def __init__(self, klass):
        self.klass = klass

    def __enter__(self):
        st.markdown(f'<div class="{self.klass}">', unsafe_allow_html=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        st.markdown("</div>", unsafe_allow_html=True)
