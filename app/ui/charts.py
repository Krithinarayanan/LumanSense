import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from app.ui.panel import PanelContainer


def render_line_chart(
    df,
    x,
    y,
    colors,
    color_by="zone",
    x_title="Time",
    y_title=None,
    width="stretch",
):
    fig = px.line(
        df,
        x=x,
        y=y,
        color=color_by,
        line_shape="spline",  # smooth lines
        markers=True,
        color_discrete_sequence=px.colors.qualitative.Bold,
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=colors["surface"],
        height=420,
        margin={"l": 15, "r": 15, "t": 20, "b": 15},
        hovermode="x unified",
        font={
            "family": "Inter",
            "size": 13,
            "color": colors["text_primary"],
        },
        legend={"orientation": "h", "y": 1.02, "x": 0, "bgcolor": "rgba(0,0,0,0)"},
        xaxis={
            "title": x_title,
            "showgrid": True,
            "gridcolor": "rgba(255,255,255,.05)",
            "showspikes": True,
            "spikecolor": colors["primary"],
            "color": colors["text_secondary"],
        },
        yaxis={
            "title": y_title,
            "showgrid": True,
            "gridcolor": "rgba(255,255,255,.05)",
            "color": colors["text_secondary"],
        },
        hoverlabel={
            "bgcolor": "#1B1F2A",
            "font": {
                "color": "#F8FAFC",
                "size": 12,
                "family": "Inter",
            },
            "align": "left",
        },
    )
    with PanelContainer("chart-container"):
        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displaylogo": False,
                "responsive": True,
            },
        )


def render_bar_chart(
    df,
    x,
    y,
    colors,
    title="",
    width="stretch",
    bar_color=None,
    value_suffix="",
):
    """Renders a flat bar chart using Plotly in Streamlit.

    Args:
        df (pd.DataFrame): Dataframe containing the chart data.
        x (str): Column name for the X axis.
        y (str): Column name for the Y axis.
        colors (dict): Dictionary of parsed CSS color variables.
        title (str, optional): Title of the bar chart. Defaults to "".
        width (str, optional): Width of the bar chart. Defaults to "stretch".
        bar_color (str, optional): Flat accent color for bars.
            Defaults to colors["accent_blue"] or "#5794F2".
        value_suffix (str, optional): Unit suffix appended to hover/labels,
            e.g. " W", "%".
    """
    if df.empty:
        return

    accent = bar_color or colors.get("accent_blue", "#5794F2")
    grid_color = colors.get("border", "rgba(255,255,255,0.09)")
    text_primary = colors.get("text_primary", "#c0c4d6")
    text_secondary = colors.get("text_secondary", "#8e94b0")

    def _fmt(v):
        """Compact number formatting (K/M abbreviations)."""
        av = abs(v)
        if av >= 1_000_000:
            s = f"{v / 1_000_000:.2f}".rstrip("0").rstrip(".") + "M"
        elif av >= 1_000:
            s = f"{v / 1_000:.2f}".rstrip("0").rstrip(".") + "K"
        else:
            s = f"{v:.2f}".rstrip("0").rstrip(".") if v % 1 else f"{int(v)}"
        return s + value_suffix

    labels = df[y].apply(_fmt)

    fig_bar = go.Figure(
        go.Bar(
            x=df[x],
            y=df[y],
            marker={
                "color": accent,
                "line": {"color": accent, "width": 0},
                "opacity": 0.85,
            },
            text=labels,
            textposition="outside",
            textfont={"color": text_secondary, "size": 11, "family": "monospace"},
            hovertemplate=f"%{{y:.2f}}{value_suffix}<extra></extra>",
            cliponaxis=False,
        )
    )

    fig_bar.update_layout(
        title={
            "text": f"<span style='letter-spacing:0.3px'>{title}</span>",
            "font": {
                "color": text_primary,
                "size": 13,
                "family": "Inter, -apple-system, sans-serif",
            },
            "x": 0.01,
            "xanchor": "left",
            "y": 0.97,
        },
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin={"l": 10, "r": 10, "t": 40, "b": 40},
        hovermode="closest",
        hoverlabel={
            "bgcolor": colors.get("surface_raised", "#22273a"),
            "bordercolor": grid_color,
            "font": {"color": text_primary, "size": 11, "family": "monospace"},
        },
        xaxis={
            "type": "category",
            "showgrid": False,
            "zeroline": False,
            "showline": False,
            "linecolor": grid_color,
            "linewidth": 1,
            "showticklabels": True,
            "tickfont": {"color": text_secondary, "size": 12, "family": "monospace"},
            "title": "Zone",
            "automargin": False,
            "showspikes": False,
        },
        yaxis={
            "showgrid": True,
            "gridcolor": grid_color,
            "gridwidth": 1,
            "griddash": "dot",
            "zeroline": False,
            "showline": False,
            "tickfont": {"color": text_secondary, "size": 10, "family": "monospace"},
            "tickformat": ".2s",
            "title": None,
            "showspikes": False,
            "rangemode": "tozero",
            "range": [0, df[y].max() * 1.2],
        },
        font={"color": text_secondary},
        bargap=0.35,
        showlegend=False,
    )

    use_container_width = width == "stretch"
    st.plotly_chart(
        fig_bar,
        use_container_width=use_container_width,
        config={"displayModeBar": False},
    )
