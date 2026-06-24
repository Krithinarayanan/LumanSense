from pandas._libs.tslibs import timestamps
import pandas as pd
import sqlite3
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LumenSense",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

BG_PAGE  = "#0f1117"
BG_CARD  = "#1a1d27" 
BG_PLOT  = "#1a1d27" 
BORDER   = "#2a2d3a" 
TEXT_PRI = "#e8eaf6" 
TEXT_SEC = "#8b8fa8" 
GRID_COL = "#2a2d3a"
TEXT_VAL = "#c0c4d6"

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
/* Global typography */
html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}

/* Hide Streamlit chrome + remove default top padding */
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ padding-top: 1rem !important; }}

/* Page background */
.stApp {{ background-color: {BG_PAGE}; }}

/* Section headers */
.section-header {{
    color: {TEXT_SEC};
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin: 32px 0 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid {BORDER};
}}

/* Zone pill badge */
.zone-badge {{
    display: inline-block;
    padding: 2px 10px;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    background: #1e2a3a;
    color: #60a5fa;
    border: 1px solid #2a4a7f;
}}

/* Dataframe overrides */
[data-testid="stDataFrame"] {{ border-radius: 10px; overflow: hidden; }}

/* Reason column wrap */
[data-testid="stDataFrame"] [role="gridcell"]:last-child {{
    white-space: normal !important;
    word-break: break-word !important;
    line-height: 1.4 !important;
}}

/* Left-align all table cells */
.stTable table thead th,
.stTable table tbody td {{
    text-align: left !important;
    white-space: nowrap !important;
}}
</style>
""", unsafe_allow_html=True)


# ── Data layer ─────────────────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def load_all_data():
    conn = sqlite3.connect("luman_sense.db")

    kpis = {
        "detection_count": conn.execute("SELECT COUNT(*) FROM detection_events").fetchone()[0],
        "decision_count":  conn.execute("SELECT COUNT(*) FROM decision_events").fetchone()[0],
        "most_active_zone": conn.execute(
            "SELECT zone FROM detection_events GROUP BY zone ORDER BY COUNT(zone) DESC LIMIT 1"
        ).fetchone()[0],
        "total_saved": conn.execute("SELECT SUM(energy_saved_watts) FROM decision_events").fetchone()[0] or 0,
    }

    pedestrian_chart = pd.read_sql_query("""
        SELECT timestamp, zone, sum(pedestrians) AS pedestrians
        FROM detection_events
        GROUP BY timestamp, zone
        ORDER BY timestamp DESC
        LIMIT 30
    """, conn)

    detection_events = pd.read_sql_query("""
        SELECT timestamp               AS "Timestamp",
               zone                   AS "Zone",
               zone_occupancy_forecast AS "Zone Occupancy Forecast",
               pedestrians            AS "Pedestrians",
               ema                    AS "EMA",
               delta_occupancy        AS "Delta Occupancy",
               trend_label            AS "Trend Label",
               cluster_label          AS "Cluster Label"
        FROM detection_events
        ORDER BY timestamp DESC
        LIMIT 30
    """, conn)

    decision_events = pd.read_sql_query("""
        SELECT timestamp           AS "Timestamp",
               zone                AS "Zone",
               state               AS "State",
               pred_brightness     AS "Brightness Plan",
               reactive_brightness AS "Reactive Brightness",
               brightness          AS "Brightness to Lamp",
               energy_saved_watts  AS "Energy Saved (W)",
               reason              AS "Reason"
        FROM decision_events
        ORDER BY timestamp DESC
        LIMIT 30
    """, conn)

    zone_summary = pd.read_sql_query("""
        SELECT
            t.zone                      AS Zone,
            SUM(t.pedestrians)          AS Pedestrians,
            COUNT(c.state)              AS Dimming_Actions_Taken,
            AVG(c.brightness)           AS Avg_Brightness,
            AVG(c.energy_saved_watts)   AS Avg_Energy_Saved
        FROM detection_events t
        LEFT JOIN decision_events c
               ON t.zone = c.zone AND t.timestamp = c.timestamp
        GROUP BY t.zone
    """, conn)

    conn.close()
    return kpis, pedestrian_chart, detection_events, decision_events, zone_summary


kpis, pedestrian_chart, detection_events, decision_events, zone_summary = load_all_data()


# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="padding: 8px 0 24px;">
    <span style="font-size: 1.6rem; font-weight: 700; color: {TEXT_PRI};">💡 LumenSense</span>
    <span style="margin-left: 12px; font-size: 0.85rem; color: {TEXT_SEC};">
        Smart Lighting Intelligence Dashboard
    </span>
</div>
""", unsafe_allow_html=True)


# ── KPI cards with icons + tooltips ───────────────────────────────────────────
lightning_optimization = (
    (kpis['detection_count'] - kpis['decision_count']) / kpis['detection_count']
) * 100

def kpi_card(col, icon, label, value, tooltip):
    col.markdown(f"""
    <div title="{tooltip}" style="
        background: {BG_CARD};
        border: 1px solid {BORDER};
        border-radius: 12px;
        padding: 20px 24px;
        cursor: default;
    ">
        <div style="font-size: 1.4rem; margin-bottom: 6px;">{icon}</div>
        <div style="
            color: {TEXT_SEC};
            font-size: 0.72rem;
            font-weight: 600;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            margin-bottom: 6px;
        ">{label}</div>
        <div style="
            color: {TEXT_PRI};
            font-size: 1.6rem;
            font-weight: 700;
            line-height: 1.1;
        ">{value}</div>
    </div>
    """, unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns(5)

kpi_card(c1, "🔍", "Detection Events",      f"{kpis['detection_count']:,}",
         "Total pedestrian detection events captured across all zones")
kpi_card(c2, "💡", "Lighting Decisions",    f"{kpis['decision_count']:,}",
         "Total brightness adjustment decisions made by the controller")
kpi_card(c3, "⚡", "Lighting Optimization", f"{lightning_optimization:.2f}%",
         "% of detection events where lighting was NOT adjusted — higher means smarter dimming")
kpi_card(c4, "📍", "<br>Most Active Zone",      kpis["most_active_zone"],
         "Zone with the highest number of pedestrian detection events")
kpi_card(c5, "🔋", "<br>Energy Saved",          f"{kpis['total_saved']:.1f} W",
         "Cumulative energy saved (watts) from all dimming decisions")


# ── Pedestrian activity chart ──────────────────────────────────────────────────
st.markdown('<br><p class="section-header">🚶 Pedestrian Activity — Last 30 Readings</p>', unsafe_allow_html=True)

if not pedestrian_chart.empty:
    fig_line = px.line(
        pedestrian_chart,
        x="timestamp",
        y="pedestrians",
        color="zone",
        markers=True,
        template="plotly_dark",
        color_discrete_sequence=px.colors.qualitative.Bold,
    )
    fig_line.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=BG_PLOT,
        legend_title_text="Zone",
        margin=dict(l=0, r=0, t=8, b=0),
        xaxis=dict(gridcolor=GRID_COL, title="Time",          color=TEXT_SEC),
        yaxis=dict(gridcolor=GRID_COL, title="# Pedestrians", color=TEXT_SEC),
        font=dict(color=TEXT_SEC),
        height=300,
    )
    st.plotly_chart(fig_line, use_container_width=True)


# ── Zone Summary ───────────────────────────────────────────────────────────────
st.markdown('<p class="section-header">📊 Zone Summary</p>', unsafe_allow_html=True)
col_table, col_heat = st.columns([3, 2], gap="large")

with col_table:
    st.dataframe(
        zone_summary,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Zone": st.column_config.TextColumn(
                "📍 Zone",
                width="small",
            ),
            "Pedestrians": st.column_config.NumberColumn(
                "🚶 Pedestrians",
                width="small",
                format="%d",
            ),
            "Dimming_Actions_Taken": st.column_config.NumberColumn(
                "📋 Dimming Actions",
                width="small",
                format="%d",
            ),
            "Avg_Brightness": st.column_config.NumberColumn(
                "🔆 Avg Brightness",
                width="small",
                format="%.2f",
            ),
            "Avg_Energy_Saved": st.column_config.NumberColumn(
                "🔋 Avg Energy Saved (W)",
                width="small",
                format="%.2f",
            ),
        },
    )

with col_heat:
    if not zone_summary.empty:
        fig_bar = go.Figure(go.Bar(
            x=zone_summary["Zone"],
            y=zone_summary["Avg_Energy_Saved"],
            marker=dict(
                color=zone_summary["Avg_Energy_Saved"],
                colorscale="Blues",
                showscale=False,
            ),
            text=zone_summary["Avg_Energy_Saved"].round(2),
            textposition="outside",
            textfont=dict(color=TEXT_VAL, size=12),
        ))
        fig_bar.update_layout(
            title=dict(
                text="🔋 Avg Energy Saved (W) by Zone",
                font=dict(color=TEXT_VAL, size=13),
                x=0,
                xanchor="left",
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor=BG_PLOT,
            margin=dict(l=0, r=0, t=36, b=0),
            xaxis=dict(
                gridcolor=GRID_COL,
                title=None,
                tickfont=dict(color=TEXT_SEC, size=12),
            ),
            yaxis=dict(
                gridcolor=GRID_COL,
                title=None,
                showticklabels=False,
            ),
            font=dict(color=TEXT_SEC),
            height=260,
            bargap=0.3,
        )
        st.plotly_chart(fig_bar, use_container_width=True)


# ── Event tables ───────────────────────────────────────────────────────────────
st.markdown('<p class="section-header">📋 Event Tables</p>', unsafe_allow_html=True)
tab1, tab2 = st.tabs(["🔍 Detection Events", "💡 Lighting Decisions"])

with tab1:
    st.dataframe(
        detection_events,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Timestamp":               st.column_config.TextColumn("🕐 Timestamp",        width="small"),
            "Zone":                    st.column_config.TextColumn("📍 Zone",              width="small"),
            "Zone Occupancy Forecast": st.column_config.NumberColumn("🔮 Occ. Forecast",  width="small", format="%.2f"),
            "Pedestrians":             st.column_config.NumberColumn("🚶 Pedestrians",     width="small", format="%d"),
            "EMA":                     st.column_config.NumberColumn("📈 EMA",             width="small", format="%.2f"),
            "Delta Occupancy":         st.column_config.NumberColumn("↕️ Δ Occupancy",    width="small", format="%.2f"),
            "Trend Label":             st.column_config.TextColumn("📊 Trend",             width="small"),
            "Cluster Label":           st.column_config.TextColumn("🧩 Cluster",           width="small"),
        },
    )

with tab2:
    st.dataframe(
        decision_events,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Timestamp":           st.column_config.TextColumn("🕐 Timestamp",        width="small"),
            "Zone":                st.column_config.TextColumn("📍 Zone",              width="small"),
            "State":               st.column_config.TextColumn("🔵 State",             width="small"),
            "Brightness Plan":     st.column_config.NumberColumn("🗓️ Plan",            width="small", format="%d%%"),
            "Reactive Brightness": st.column_config.NumberColumn("⚡ Reactive",        width="small", format="%d%%"),
            "Brightness to Lamp":  st.column_config.NumberColumn("💡 To Lamp",         width="small", format="%d%%"),
            "Energy Saved (W)":    st.column_config.NumberColumn("🔋 Energy (W)",      width="small", format="%.2f"),
            "Reason":              st.column_config.TextColumn("📝 Reason",             width="large"),
        },
    )