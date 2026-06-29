
import streamlit as st

def render_table(df, column_config: dict):
    """Renders a generic table using Streamlit.

    Args:
        df (pd.DataFrame): Dataframe containing the table data.
        column_config (dict): Dictionary of column configurations.
    """
    col_table, col_heat = st.columns([3, 2], gap="large")
    with col_table:
        st.dataframe(
            df, use_container_width=True, hide_index=True,
            column_config={
                "Zone":                  st.column_config.TextColumn("📍 Zone",                    width="small"),
                "Pedestrians":           st.column_config.NumberColumn("🚶 Pedestrians",            width="small", format="%d"),
                "Dimming_Actions_Taken": st.column_config.NumberColumn("📋 Dimming Actions",        width="small", format="%d"),
                "Avg_Brightness":        st.column_config.NumberColumn("🔆 Avg Brightness",         width="small", format="%.2f"),
                "Total_Energy_Saved":    st.column_config.NumberColumn("🔋 Total Energy Saved (W)", width="small", format="%.2f"),
            },
        )