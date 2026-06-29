import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

def render_line_chart(df, x, y, colors, color_by="zone", x_title="Time", y_title=None):
    """Renders a generic line chart using Plotly Express in Streamlit.

    Args:
        df (pd.DataFrame): Dataframe containing the chart data.
        x (str): Column name for the X axis.
        y (str): Column name for the Y axis.
        colors (dict): Dictionary of parsed CSS color variables.
        color_by (str, optional): Column name to group/color lines. Defaults to "zone".
        x_title (str, optional): Title for the X axis. Defaults to "Time".
        y_title (str, optional): Title for the Y axis. Defaults to None.
    """
    if not df.empty:
        fig_line = px.line(
            df, x=x, y=y, color=color_by,
            markers=True, template="plotly_dark",
            color_discrete_sequence=px.colors.qualitative.Bold,
        )
        fig_line.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor=colors.get("BG_PLOT", "#1a1d27"),
            legend_title_text=color_by.capitalize() if color_by else None,
            margin=dict(l=0, r=0, t=8, b=0),
            xaxis=dict(
                gridcolor=colors.get("GRID_COL", "#1e2130"),
                title=x_title,
                color=colors.get("TEXT_SEC", "#6b7094"),
            ),
            yaxis=dict(
                gridcolor=colors.get("GRID_COL", "#1e2130"),
                title=y_title if y_title is not None else y.capitalize(),
                color=colors.get("TEXT_SEC", "#6b7094"),
            ),
            font=dict(color=colors.get("TEXT_SEC", "#6b7094")),
            height=300,
        )
        st.plotly_chart(fig_line, use_container_width=True)

def render_bar_chart(df, x, y, colors, title="", height=260):
    """Renders a generic bar chart using Plotly Graphical Objects in Streamlit.

    Args:
        df (pd.DataFrame): Dataframe containing the chart data.
        x (str): Column name for the X axis.
        y (str): Column name for the Y axis.
        colors (dict): Dictionary of parsed CSS color variables.
        title (str, optional): Title of the bar chart. Defaults to "".
        height (int, optional): Height of the bar chart. Defaults to 260.
    """
    col_table, col_heat = st.columns([3, 2], gap="large")
    with col_heat:
        if not df.empty:
            fig_bar = go.Figure(go.Bar(
                x=df[x], y=df[y],
                marker=dict(color=df[y], colorscale="Blues", showscale=False),
                text=df[y].round(2),
                textposition="outside", textfont=dict(color=colors.get("TEXT_VAL", "#c0c4d6"), size=12),
            ))
            fig_bar.update_layout(
                title=dict(text=title,
                           font=dict(color=colors.get("TEXT_VAL", "#c0c4d6"), size=13), x=0, xanchor="left"),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=colors.get("BG_PLOT", "#1a1d27"),
                margin=dict(l=0, r=0, t=36, b=0),
                xaxis=dict(gridcolor=colors.get("GRID_COL", "#1e2130"), title=None, tickfont=dict(color=colors.get("TEXT_SEC", "#6b7094"), size=12)),
                yaxis=dict(gridcolor=colors.get("GRID_COL", "#1e2130"), title=None, showticklabels=False),
                font=dict(color=colors.get("TEXT_SEC", "#6b7094")), height=height, bargap=0.3,
            )
            st.plotly_chart(fig_bar, use_container_width=True)

