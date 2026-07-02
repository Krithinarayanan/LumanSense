from app.ui import charts


def render_pedestrian_chart(pedestrian_chart, colors={}):
    charts.render_line_chart(
        pedestrian_chart, x="timestamp", y="pedestrians", color_by="zone", colors=colors
    )


def render_energy_chart(zone_summary, colors={}):
    charts.render_bar_chart(
        zone_summary,
        x="Zone",
        y="Total_Energy_Saved",
        colors=colors,
        title="🔋 Energy Saved by Zone",
    )
