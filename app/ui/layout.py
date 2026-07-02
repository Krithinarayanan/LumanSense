"""Layout helper module.

This module provides wrappers for Streamlit columns, tabs, and column configurations.
"""

from typing import Any

import streamlit as st
from streamlit.delta_generator import DeltaGenerator


def columns(number, gap="small") -> list[DeltaGenerator]:
    return st.columns(number, gap=gap)


def tabs(tabs) -> list[DeltaGenerator]:
    return st.tabs(tabs)


def text_column(label: str, width: str) -> Any:
    return st.column_config.TextColumn(label, width=width)


def number_column(label: str, width: str, format: str) -> Any:
    return st.column_config.NumberColumn(label, width=width, format=format)


def progress_column(label: str, width: str, format: str) -> Any:
    return st.column_config.ProgressColumn(label, width=width, format=format)
