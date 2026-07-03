from app.ui import layout
from app.ui.cards import kpi_card
from app.ui.panel import PanelContainer

DETECTION_ICON = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="11" cy="11" r="8"></circle>
  <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
</svg>"""

DECISION_ICON = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A5 5 0 0 0 8 8c0 1 .3 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5"></path>
  <line x1="9" y1="18" x2="15" y2="18"></line>
  <line x1="10" y1="22" x2="14" y2="22"></line>
</svg>"""

OPTIMIZATION_ICON = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
</svg>"""

ACTIVE_ZONE_ICON = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
  <circle cx="12" cy="10" r="3"></circle>
</svg>"""

ENERGY_ICON = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <rect x="1" y="6" width="18" height="12" rx="2" ry="2"></rect>
  <line x1="23" y1="11" x2="23" y2="13"></line>
</svg>"""


def build_dashboard_cards(kpis):
    lightning_optimization = (
        100
        * (kpis["detection_count"] - kpis["decision_count"])
        / kpis["detection_count"]
    )
    c1, c2, c3, c4, c5 = layout.columns(5, gap="small")
    with PanelContainer("dashboard-container"):
        kpi_card(
            c1,
            DETECTION_ICON,
            "Detection Events",
            f"{kpis['detection_count']:,}",
            "Total pedestrian detection events captured across all zones",
        )
        kpi_card(
            c2,
            DECISION_ICON,
            "Controller Decisions",
            f"{kpis['decision_count']:,}",
            "Total brightness adjustment decisions made by the controller",
        )
        kpi_card(
            c3,
            OPTIMIZATION_ICON,
            "Optimization Rate",
            f"{lightning_optimization:.2f}%",
            "% of detection events where lighting was NOT adjusted — higher = smarter",
        )
        kpi_card(
            c4,
            ACTIVE_ZONE_ICON,
            "Most Active Zone",
            kpis["most_active_zone"],
            "Zone with the highest number of pedestrian detection events",
        )
        kpi_card(
            c5,
            ENERGY_ICON,
            "Energy Saved",
            f"{kpis['total_saved']:.2f} W",
            "Cumulative energy saved (watts) from all dimming decisions",
        )
