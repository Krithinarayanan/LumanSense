from app.ui import layout, tables


def render_zone_summary_table(zone_summary, column_config):
    tables.render_table(zone_summary, column_config)


def render_detection_decision_tables(
    tabs,
    detection_events,
    decision_events,
    detection_column_config,
    decision_column_config,
):
    tab1, tab2 = layout.tabs(tabs)
    tables.render_table(detection_events, detection_column_config, tab1)
    tables.render_table(decision_events, decision_column_config, tab2)
