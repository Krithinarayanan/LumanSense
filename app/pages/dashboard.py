from app.mcp.database_mcp import load_all_data
from app.ui.cards import kpi_card
from app.ui.sidecard import render_sidebar
import streamlit as st
from app.ui.theme import apply_theme, get_theme_colors
from app.ui.charts import render_line_chart, render_bar_chart
from app.ui.tables import render_table

st.set_page_config(
    page_title="LumenSense",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="expanded",
)
print("apply theme")
apply_theme()

colors = get_theme_colors()
print("load all data")
# ── Data layer ─────────────────────────────────────────────────────────────────

kpis, pedestrian_chart, detection_events, decision_events, zone_summary = load_all_data()
print("render sidebar")
render_sidebar("dashboard")
print("page header")
# ── Page header ────────────────────────────────────────────────────────────────
lightning_optimization = (
    (kpis['detection_count'] - kpis['decision_count']) / kpis['detection_count']
) * 100

st.markdown("""
<div class="page-header-container">
    <span class="page-header-title">Dashboard</span>
    <span class="page-header-subtitle">Real-time lighting intelligence overview</span>
</div>
""", unsafe_allow_html=True)

# ── KPI cards ──────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5, gap="small")
kpi_card(c1, "🔍", "Detection Events",      f"{kpis['detection_count']:,}",
         "Total pedestrian detection events captured across all zones", "blue")
kpi_card(c2, "💡", "Lighting Decisions",    f"{kpis['decision_count']:,}",
         "Total brightness adjustment decisions made by the controller", "indigo")
kpi_card(c3, "⚡", "Optimization Rate",     f"{lightning_optimization:.1f}%",
         "% of detection events where lighting was NOT adjusted — higher = smarter", "green")
kpi_card(c4, "📍", "Most Active Zone",       kpis["most_active_zone"],
         "Zone with the highest number of pedestrian detection events", "yellow")
kpi_card(c5, "🔋", "Energy Saved",           f"{kpis['total_saved']:.1f} W",
         "Cumulative energy saved (watts) from all dimming decisions", "pink")

# ── Pedestrian chart ───────────────────────────────────────────────────────────
st.markdown('<p class="section-header">🚶 Pedestrian Activity — Last 30 Readings</p>', unsafe_allow_html=True)
render_line_chart(
    pedestrian_chart,
    x="timestamp",
    y="pedestrians",
    colors=colors,
    color_by="zone",
    x_title="Time",
    y_title="# Pedestrians",
)


# ── Zone summary ───────────────────────────────────────────────────────────────
st.markdown('<p class="section-header">📊 Zone Summary</p>', unsafe_allow_html=True)
render_table(zone_summary, {
    "Zone":                  st.column_config.TextColumn("📍 Zone",                    width="small"),
    "Pedestrians":           st.column_config.NumberColumn("🚶 Pedestrians",            width="small", format="%d"),
    "Dimming_Actions_Taken": st.column_config.NumberColumn("📋 Dimming Actions",        width="small", format="%d"),
    "Avg_Brightness":        st.column_config.NumberColumn("🔆 Avg Brightness",         width="small", format="%.2f"),
    "Total_Energy_Saved":    st.column_config.NumberColumn("🔋 Total Energy Saved (W)", width="small", format="%.2f"),
})


render_bar_chart(
    zone_summary,
    x="Zone",
    y="Total_Energy_Saved",
    colors=colors,
    title="🔋 Energy Saved by Zone",
)

# ── Event tables ───────────────────────────────────────────────────────────────
st.markdown('<p class="section-header">📋 Event Tables</p>', unsafe_allow_html=True)
tab1, tab2 = st.tabs(["🔍 Detection Events", "💡 Lighting Decisions"])
with tab1:
    render_table(detection_events, {"Timestamp":               st.column_config.TextColumn("🕐 Timestamp",       width="small"),
            "Zone":                    st.column_config.TextColumn("📍 Zone",             width="small"),
            "Zone Occupancy Forecast": st.column_config.NumberColumn("🔮 Occ. Forecast", width="small", format="%.2f"),
            "Pedestrians":             st.column_config.NumberColumn("🚶 Pedestrians",    width="small", format="%d"),
            "EMA":                     st.column_config.NumberColumn("📈 EMA",            width="small", format="%.2f"),
            "Delta Occupancy":         st.column_config.NumberColumn("↕️ Δ Occupancy",   width="small", format="%.2f"),
            "Trend Label":             st.column_config.TextColumn("📊 Trend",            width="small"),
            "Cluster Label":           st.column_config.TextColumn("🧩 Cluster",          width="small"),})
with tab2:
    render_table(decision_events, {"Timestamp":           st.column_config.TextColumn("🕐 Timestamp",       width="small"),
            "Zone":                st.column_config.TextColumn("📍 Zone",             width="small"),
            "State":               st.column_config.TextColumn("🔵 State",            width="small"),
            "Brightness Plan":     st.column_config.NumberColumn("🗓️ Plan",           width="small", format="%d%%"),
            "Reactive Brightness": st.column_config.NumberColumn("⚡ Reactive",       width="small", format="%d%%"),
            "Brightness to Lamp":  st.column_config.NumberColumn("💡 To Lamp",        width="small", format="%d%%"),
            "Energy Saved (W)":    st.column_config.NumberColumn("🔋 Energy (W)",     width="small", format="%.2f"),
            "Reason":              st.column_config.TextColumn("📝 Reason",            width="large"),
            "Cluster Label":       st.column_config.TextColumn("🧩 Cluster",           width="small"),
        },
    )