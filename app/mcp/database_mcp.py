import sqlite3

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("DatabaseMCP")

DB_FILE = "luman_sense.db"


def get_connection():
    return sqlite3.connect(DB_FILE)


@mcp.tool()
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

    conn.commit()
    conn.close()


@mcp.tool()
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
        (timestamp, zone, pedestrians, ema, trend_label, zone_occupancy_forecast, delta_occupancy, cluster_label)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (timestamp, zone, pedestrians, ema, trend_label, zone_occupancy_forecast, delta_occupancy, cluster_label),
    )
    conn.commit()
    conn.close()


@mcp.tool()
def save_decision_event(
    event={}
):
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
        (timestamp, zone, state, pred_brightness, reactive_brightness , brightness, energy_saved_watts, reason)
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


def get_detection_event(limit=80):
    # query from detection event table last limit records
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT * FROM detection_events ORDER BY timestamp DESC LIMIT ?
        """,
        (limit,),
    )
    rows = cursor.fetchall()
    conn.close()

    print("\n[DETECTION EVENTS]")
    print("Time | Zone | Pedestrians | EMA")

    for e in rows:
        print(
            e["timestamp"],
            e["zone"],
            e["pedestrians"],
            f"{e['ema']:.2f}",
            f"{e['cluster_label']}",
        )
    return [dict(row) for row in rows]

def get_decision_event(limit=80):
    # query from decision event table last limit records
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT * FROM decision_events ORDER BY timestamp DESC LIMIT ?
        """,
        (limit,),
    )

    print("\n[DECISION EVENTS]")
    print("Time | Zone |          State        | Brightness | Energy Saved (Watts)")

    rows = cursor.fetchall()

    for e in rows:
        print(
            e["timestamp"],
            e["zone"],
            e["state"],
            f"{e['brightness']:.2f}",
            f"{e['energy_saved_watts']:.2f}",
        )

    conn.close()
    return [dict(row) for row in rows]


def get_total_detection_events():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT zone, COUNT(pedestrians) as count FROM detection_events group by zone")
    result = cursor.fetchall()
    conn.close()
    return result


def get_total_decision_events():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT zone, COUNT(timestamp) as count FROM decision_events group by zone")
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


@mcp.tool()
def get_average_pedestrians():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT AVG(pedestrians) FROM detection_events")
    result = cursor.fetchone()
    conn.close()
    return result[0]


@mcp.tool()
def get_total_energy_saved():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(energy_saved_watts) FROM decision_events")
    result = cursor.fetchone()
    conn.close()
    return result[0]


@mcp.tool()
def fetch_analytics():
    """Fetches and prints system analytics."""
    try:
        get_detection_event()
        get_decision_event()
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
