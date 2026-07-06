import app.pages.dashboard_ui_helper as helper
import app.ui.components.dashboard.charts as charts
import app.ui.components.dashboard.tables as tables
from app.mcp import database_mcp as mcp
from app.ui import layout, theme, typography

zone_summary_column_config = {
    "Zone": layout.text_column("Zone", width="small"),
    "Pedestrians": layout.number_column("Pedestrians", width="small", format="%d"),
    "Dimming_Actions_Taken": layout.number_column(
        "Dimming Actions", width="small", format="%d"
    ),
    "Avg_Brightness": layout.progress_column(
        "Avg Brightness", width="small", format="%.2f"
    ),
    "Total_Energy_Saved": layout.number_column(
        "Total Energy Saved (W)", width="small", format="%.2f"
    ),
    "Total_CO2_Saved": layout.number_column(
        "Total CO2 Saved (g)", width="small", format="%.3f"
    ),
}

detection_table_column_config = {
    "Timestamp": layout.text_column("Timestamp", width="small"),
    "Zone": layout.text_column("Zone", width="small"),
    "Zone Occupancy Forecast": layout.number_column(
        "Occ. Forecast", width="small", format="%.2f"
    ),
    "Pedestrians": layout.number_column("Pedestrians", width="small", format="%d"),
    "EMA": layout.number_column("EMA", width="small", format="%.2f"),
    "Delta Occupancy": layout.number_column("Occupancy", width="small", format="%.2f"),
    "Trend Label": layout.text_column("Trend", width="small"),
    "Cluster Label": layout.text_column("Cluster", width="small"),
}

decision_table_column_config = {
    "Timestamp": layout.text_column("Timestamp", width="small"),
    "Zone": layout.text_column("Zone", width="small"),
    "State": layout.text_column("State", width="small"),
    "Brightness Plan": layout.number_column("Plan", width="small", format="%d%%"),
    "Reactive Brightness": layout.number_column(
        "Reactive", width="small", format="%d%%"
    ),
    "Brightness to Lamp": layout.number_column("To Lamp", width="small", format="%d%%"),
    "Energy Saved (W)": layout.number_column(
        "Energy (W)", width="small", format="%.2f"
    ),
    "Carbon Intensity (g/kWh)": layout.number_column(
        "CO2 Intensity", width="small", format="%.2f"
    ),
    "CO2 Saved (g)": layout.number_column(
        "CO2 Saved (g)", width="small", format="%.3f"
    ),
    "Reason": layout.text_column("Reason", width="large"),
}


def render_dashboard():
    typography.configure_page(
        "lumanSense", "💡", "Real-time lighting intelligence overview"
    )

    theme.apply_theme("base.css", "dashboard.css", "tables.css")

    typography.render_page_header(
        "Dashboard", "Real-time lighting intelligence overview"
    )
    kpis, pedestrian_chart, detection_events, decision_events, zone_summary = (
        mcp.load_all_data()
    )
    helper.build_dashboard_cards(kpis)

    typography.render_section_header("🚶 Pedestrian Activity — Last 30 Readings")
    charts.render_pedestrian_chart(pedestrian_chart, colors=theme.THEME_COLORS)

    typography.render_section_header("📊 Zone Summary")
    tables.render_zone_summary_table(zone_summary, zone_summary_column_config)
    typography.render_section_header("⚡ Energy Consumption by Zone — Last 30 Readings")
    charts.render_energy_chart(zone_summary, colors=theme.THEME_COLORS)
    typography.render_section_header("📋 Event Tables")
    tabs = ["🔍 Detection Events", "💡 Lighting Decisions"]
    tables.render_detection_decision_tables(
        tabs,
        detection_events,
        decision_events,
        detection_table_column_config,
        decision_table_column_config,
    )
