def kpi_card(col, icon, label, value, tooltip):
    col.markdown(
        f"""
        <div class="kpi-card">
        <div class="card-header"><span class="card-icon">{icon}</span> {label}</div>
        <div class="card-value">{value}</div>
    """,
        unsafe_allow_html=True,
    )
