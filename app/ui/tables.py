import pandas as pd
import streamlit as st

# Add to ICONS dict Timestamp	📍 Zone	State	Plan	Reactive	To Lamp	Energy (W)	Reason
ICONS = {
    "Zone": "📍",
    "Pedestrians": "🚶",
    "Dimming Actions": "📋",
    "Avg Brightness": "☀️",
    "Total Energy Saved (W)": "🔋",
    "Timestamp": "🕒",
    "State": "🔄",
    "Plan": "📈",
    "Reactive": "🎯",
    "To Lamp": "💡",
    "Energy (W)": "⚡",
    "Reason": "💬",
    "Occ. Forecast": "👣",
    "EMA": "📊",
    "Occupancy": "👥",
    "Trend": "↕️",
    "Cluster": "🧩",
}


def _type_config(col_cfg):
    """Best-effort extraction of the type_config sub-dict from a
    st.column_config.* entry."""
    if not isinstance(col_cfg, dict):
        return {}
    return col_cfg.get("type_config", {}) or {}


def _col_type(col_cfg):
    return _type_config(col_cfg).get("type", "")


def _col_label(col_cfg, fallback):
    if isinstance(col_cfg, dict):
        return col_cfg.get("label") or fallback
    return fallback


def _get_pct_class(val):
    if val < 40:
        return "value-good"
    elif val > 70:
        return "value-crit"
    else:
        return "value-warn"


def _format_value(val, col_cfg):
    fmt = _type_config(col_cfg).get("format")
    if fmt and isinstance(val, (int, float)):
        try:
            # streamlit format strings are printf-style, e.g. "%.2f"
            return fmt % val
        except TypeError:
            pass
    if isinstance(val, float):
        return f"{val:,.2f}"
    if isinstance(val, int):
        return f"{val:,}"
    return str(val)


def _render_html_table(df: pd.DataFrame, column_config: dict):
    column_config = column_config or {}

    # ---- header row ----
    header_cells = []
    for c in df.columns:
        cfg = column_config.get(c, {})
        label = _col_label(cfg, c)
        icon = ICONS.get(label.strip(), "")
        is_progress = _col_type(cfg) == "progress"
        is_numeric = pd.api.types.is_numeric_dtype(df[c]) and not is_progress

        if is_progress:
            cls = "progress"
        elif is_numeric:
            cls = "numeric"
        else:
            cls = "text"

        header_cells.append(f'<th class="{cls}">{icon} {label}</th>'.strip())
    header_html = "".join(header_cells)

    # ---- body rows ----
    row_html_list = []
    for _, row in df.iterrows():
        cells = []
        for c in df.columns:
            cfg = column_config.get(c, {})
            val = row[c]
            ctype = _col_type(cfg)

            if ctype == "progress":
                tcfg = _type_config(cfg)
                min_v = tcfg.get("min_value")
                max_v = tcfg.get("max_value")
                min_v = 0 if min_v is None else min_v
                max_v = 100 if max_v is None else max_v
                span = (max_v - min_v) or 1
                pct = max(0, min(100, ((float(val) - min_v) / span) * 100))
                pct_class = _get_pct_class(val)
                label = f'<span class="{pct_class}">{pct:.1f}%</span>'
                cells.append(
                    f'<td><div class="luman-bar-cell">'
                    f'<div class="luman-bar-track"><div class="luman-bar-fill-{pct_class}" '
                    f'style="width:{pct:.1f}%"></div></div>'
                    f'<span class="luman-bar-label">{label}</span>'
                    f"</div></td>"
                )
            elif pd.api.types.is_numeric_dtype(df[c]):
                cells.append(f'<td class="numeric">{_format_value(val, cfg)}</td>')
            else:
                cells.append(f"<td>{val}</td>")
        row_html_list.append(f"<tr>{''.join(cells)}</tr>")

    table_html = f"""
    <div class="table-frame-wrapper">
      <table class="table-frame">
        <thead><tr>{header_html}</tr></thead>
        <tbody>{"".join(row_html_list)}</tbody>
      </table>
    </div>
    """
    st.markdown(table_html, unsafe_allow_html=True)


def render_table(df, column_config, tab=None, width="stretch"):
    """Renders a generic table using Streamlit.

    Args:
        df (pd.DataFrame): Dataframe containing the table data.
        column_config (dict): Dictionary of column configurations
            (st.column_config.* entries, e.g. ProgressColumn, NumberColumn).
        tab: optional Streamlit tab/container to render inside.
        width: kept for API compatibility, unused by the HTML table.
    """

    if not tab:
        _render_html_table(df, column_config)
    else:
        with tab:
            _render_html_table(df, column_config)
