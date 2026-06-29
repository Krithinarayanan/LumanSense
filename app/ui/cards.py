def kpi_card(col, icon, label, value, tooltip, accent="blue"):
    col.markdown(f"""
    <div title="{tooltip}" class="kpi-card {accent}">
        <div class="kpi-card-icon">{icon}</div>
        <div class="kpi-card-label">{label}</div>
        <div class="kpi-card-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)