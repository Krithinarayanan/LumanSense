import os
import sqlite3
from typing import TYPE_CHECKING

# FastMCP is initialized dynamically to separate database access from the RPC layer.
if TYPE_CHECKING:
    from mcp.server.fastmcp import FastMCP

_mcp_instance = None


def _get_mcp() -> "FastMCP":
    global _mcp_instance
    if _mcp_instance is None:
        from mcp.server.fastmcp import FastMCP

        _mcp_instance = FastMCP("DatabaseMCP")
    return _mcp_instance


_current_dir = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.abspath(os.path.join(_current_dir, "../../luman_sense.db"))


def get_connection():
    return sqlite3.connect(DB_FILE)


# ── Core Database Operations ──


def setup_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS detection_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            zone TEXT,
            pedestrians INTEGER,
            ema REAL,
            trend_label TEXT,
            zone_occupancy_forecast REAL,
            delta_occupancy REAL,
            cluster_label TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS decision_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            zone TEXT,
            state TEXT,
            pred_brightness INTEGER,
            reactive_brightness INTEGER,
            brightness INTEGER,
            reason TEXT,
            energy_saved_watts INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS zone_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            zone TEXT,
            forecast REAL,
            brightness INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trained_cluster_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            cluster_id INTEGER,
            zone TEXT,
            pedestrians REAL,
            ema REAL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS zone_centroids_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cluster_index INTEGER,
            zone TEXT,
            pedestrians REAL,
            ema REAL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS footfall_predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            zone TEXT,
            probability REAL,
            brightness INTEGER
        )
    """)

    conn.commit()
    conn.close()


def save_detection_event(event={}):
    conn = get_connection()
    if event is not None:
        if isinstance(event, dict):
            timestamp = event.get("timestamp")
            zone = event.get("zone")
            pedestrians = event.get("pedestrians")
            ema = event.get("ema")
            cluster_label = event.get("cluster_label")
            trend_label = event.get("trend_label")
            zone_occupancy_forecast = event.get("zone_occupancy_forecast")
            delta_occupancy = event.get("delta")
        else:
            timestamp = event.timestamp
            zone = event.zone
            pedestrians = event.pedestrians
            ema = event.ema
            cluster_label = event.cluster_label
            trend_label = event.trend_label
            zone_occupancy_forecast = event.zone_occupancy_forecast
            delta_occupancy = event.delta

    conn.execute(
        """
        INSERT INTO detection_events
            (timestamp, zone, pedestrians, ema, trend_label,
             zone_occupancy_forecast, delta_occupancy, cluster_label)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            timestamp,
            zone,
            pedestrians,
            ema,
            trend_label,
            zone_occupancy_forecast,
            delta_occupancy,
            cluster_label,
        ),
    )
    conn.commit()
    conn.close()


def save_decision_event(event={}):
    conn = get_connection()
    if event is not None:
        if isinstance(event, dict):
            timestamp = event.get("timestamp")
            zone = event.get("zone")
            state = event.get("state")
            brightness_plan = event.get("brightness_plan")
            reactive_brightness = event.get("reactive_brightness")
            brightness_to_lamp = event.get("brightness_to_lamp")
            energy_saved_watts = event.get("energy_saved_watts")
            reason = event.get("reason")
        else:
            timestamp = event.timestamp
            zone = event.zone
            state = getattr(event, "state", getattr(event, "event_type", None))
            if (
                state is not None
                and not isinstance(state, str)
                and hasattr(state, "name")
            ):
                state = state.name
            brightness_plan = event.brightness_plan
            reactive_brightness = event.reactive_brightness
            brightness_to_lamp = event.brightness_to_lamp
            energy_saved_watts = event.energy_saved_watts
            reason = event.reason

    conn.execute(
        """
        INSERT INTO decision_events
            (timestamp, zone, state, pred_brightness, reactive_brightness,
             brightness, energy_saved_watts, reason)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            str(timestamp),
            zone,
            state,
            brightness_plan,
            reactive_brightness,
            brightness_to_lamp,
            energy_saved_watts,
            reason,
        ),
    )
    conn.commit()
    conn.close()


def save_footfall_predictions(zone, probability, brightness):
    conn = get_connection()
    conn.execute(
        "INSERT INTO footfall_predictions (zone, probability, brightness) VALUES (?, ?, ?)",
        (zone, probability, brightness),
    )
    conn.execute(
        "INSERT INTO zone_config (zone, forecast, brightness) VALUES (?, ?, ?)",
        (zone, probability, brightness),
    )
    conn.commit()
    conn.close()


def save_cluster_training_history(item: dict):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO trained_cluster_data (timestamp, cluster_id, zone, pedestrians, ema) VALUES (?, ?, ?, ?, ?)",
        (
            item["timestamp"],
            item["cluster_id"],
            item["zone"],
            item["pedestrians"],
            item["ema"],
        ),
    )
    conn.commit()
    conn.close()


def get_traffic_training_history(zone):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM trained_cluster_data WHERE zone = ? ORDER BY timestamp DESC",
        (zone,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_detection_event(limit=80):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM detection_events ORDER BY timestamp DESC LIMIT ?",
        (limit,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_decision_event(limit=80):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM decision_events ORDER BY timestamp DESC LIMIT ?",
        (limit,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# Reference mapping for zone decision queries
get_decision_events = get_decision_event


def get_detection_events_by_zone(zone: str, limit=80):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM detection_events WHERE zone = ? ORDER BY timestamp DESC LIMIT ?",
        (zone, limit),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_decision_events_by_zone(zone: str, limit=80):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM decision_events WHERE zone = ? ORDER BY timestamp DESC LIMIT ?",
        (zone, limit),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_total_detection_events():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT zone, COUNT(pedestrians) as count FROM detection_events GROUP BY zone"
    )
    result = cursor.fetchall()
    conn.close()
    return result


def get_total_decision_events():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT zone, COUNT(timestamp) as count FROM decision_events GROUP BY zone"
    )
    result = cursor.fetchall()
    conn.close()
    return result


def get_most_active_zone():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT zone, COUNT(*) as count
        FROM detection_events
        GROUP BY zone
        ORDER BY count DESC
        LIMIT 1
        """
    )
    result = cursor.fetchone()
    conn.close()
    return result


def get_average_pedestrians():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT AVG(pedestrians) FROM detection_events")
    result = cursor.fetchone()
    conn.close()
    return result[0]


def get_total_energy_saved():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(energy_saved_watts) FROM decision_events")
    result = cursor.fetchone()
    conn.close()
    return result[0]


def get_zone_config(zone: str):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM zone_config WHERE zone = ?", (zone,))
    result = cursor.fetchone()
    conn.close()
    return {} if result is None else dict(result)


def fetch_analytics():
    """Fetches and prints system analytics."""
    try:
        total_detections = get_total_detection_events()
        total_decisions = get_total_decision_events()
        active_zone_result = get_most_active_zone()
        active_zone = active_zone_result[0] if active_zone_result else "N/A"
        active_zone_count = active_zone_result[1] if active_zone_result else 0
        avg_pedestrians = get_average_pedestrians()
        total_energy = get_total_energy_saved()

        print("\n" + "=" * 40)
        print("LUMAN-SENSE SYSTEM ANALYTICS")
        print("=" * 40)
        print(f"Total Detection Events: {total_detections}")
        print(f"Total Decision Events:  {total_decisions}")
        print(f"Most Active Zone:       {active_zone} ({active_zone_count} events)")
        print(f"Average Pedestrians:    {avg_pedestrians:.2f} per Zone")
        print(f"Total Energy Saved:     {total_energy:.2f} Watts")
        print("=" * 40 + "\n")
    except Exception as e:
        print(f"Error fetching analytics: {e}")


def load_all_data():
    import pandas as pd

    conn = get_connection()
    kpis = {
        "detection_count": conn.execute(
            "SELECT COUNT(*) FROM detection_events"
        ).fetchone()[0],
        "decision_count": conn.execute(
            "SELECT COUNT(*) FROM decision_events"
        ).fetchone()[0],
        "most_active_zone": conn.execute(
            "SELECT zone FROM detection_events GROUP BY zone ORDER BY COUNT(zone) DESC LIMIT 1"
        ).fetchone()[0],
        "total_saved": conn.execute(
            "SELECT SUM(energy_saved_watts) FROM decision_events"
        ).fetchone()[0]
        or 0,
    }
    pedestrian_chart = pd.read_sql_query(
        """
        SELECT timestamp, zone, sum(pedestrians) AS pedestrians
        FROM detection_events GROUP BY timestamp, zone
        ORDER BY timestamp DESC LIMIT 30
    """,
        conn,
    )
    detection_events = pd.read_sql_query(
        """
        SELECT timestamp AS "Timestamp", zone AS "Zone",
               zone_occupancy_forecast AS "Zone Occupancy Forecast",
               pedestrians AS "Pedestrians", ema AS "EMA",
               delta_occupancy AS "Delta Occupancy",
               trend_label AS "Trend Label", cluster_label AS "Cluster Label"
        FROM detection_events ORDER BY timestamp DESC LIMIT 30
    """,
        conn,
    )
    decision_events = pd.read_sql_query(
        """
        SELECT timestamp AS "Timestamp", zone AS "Zone", state AS "State",
               pred_brightness AS "Brightness Plan",
               reactive_brightness AS "Reactive Brightness",
               brightness AS "Brightness to Lamp",
               energy_saved_watts AS "Energy Saved (W)",
               reason AS "Reason"
        FROM decision_events ORDER BY timestamp DESC LIMIT 30
    """,
        conn,
    )
    zone_summary = pd.read_sql_query(
        """
        SELECT t.zone AS Zone, SUM(t.pedestrians) AS Pedestrians,
               COUNT(c.state) AS Dimming_Actions_Taken,
               AVG(c.brightness) AS Avg_Brightness,
               SUM(c.energy_saved_watts) AS Total_Energy_Saved
        FROM detection_events t
        LEFT JOIN decision_events c ON t.zone=c.zone AND t.timestamp=c.timestamp
        GROUP BY t.zone
    """,
        conn,
    )
    conn.close()
    return kpis, pedestrian_chart, detection_events, decision_events, zone_summary


# ── Database Service Entrypoint ──
if __name__ == "__main__":
    mcp = _get_mcp()

    mcp.tool()(setup_database)
    mcp.tool()(save_detection_event)
    mcp.tool()(save_decision_event)
    mcp.tool()(save_footfall_predictions)
    mcp.tool()(get_traffic_training_history)
    mcp.tool()(get_detection_event)
    mcp.tool()(get_average_pedestrians)
    mcp.tool()(get_total_energy_saved)
    mcp.tool()(get_zone_config)
    mcp.tool()(fetch_analytics)
    mcp.tool()(load_all_data)

    mcp.run()
