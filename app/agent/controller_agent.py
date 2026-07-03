"""Controller agent module.

This module defines the LumanSense Controller Agent, which manages real-time light
brightness adjustments based on detected motion events and hysteresis rules.
"""

from datetime import datetime

from google.adk import Agent
from google.adk.models import Gemini
from google.adk.tools import ToolContext

from app.agent.brightness_planner_agent import (
    brightness_planner_agent,
    plan_brightness_for_steps,
)
from app.events.decision_event import DecisionEvent
from app.events.event_bus import event_queue
from app.events.event_types import EventType
from app.mcp.database_mcp import save_decision_event, save_detection_event
from app.mcp.database_mcp import setup_database as _setup_database
from app.mcp.energy_service import calculate_energy_saved

brightness_plan = {}
cluster_discovery_map = {}
centroids = {}


def get_decision_reason(event_type: EventType, pedestrians: int) -> str:
    """Returns a user-friendly description of the reasons leading to the decision.

    Args:
        event_type: The EventType classifying the pedestrian activity.
        pedestrians: The number of detected pedestrians.

    Returns:
        A string describing the reason for the brightness decision.
    """

    if event_type == EventType.PEAK_FORMING:
        return (
            "Pedestrian count is significantly above the EMA baseline "
            "and traffic is increasing."
        )

    if event_type == EventType.PEDESTRIAN_SPIKE:
        return "Pedestrian count is significantly above the EMA baseline."

    if event_type == EventType.CLEARING:
        return (
            "Pedestrian count is significantly below the EMA baseline "
            "and traffic is decreasing."
        )
    if event_type == EventType.LOW_ACTIVITY:
        if pedestrians < 3:
            return "Pedestrian count below low-activity threshold."
        return "Pedestrian count below expected EMA baseline."

    if event_type == EventType.NORMAL_ACTIVITY:
        return "Pedestrian count is within the expected EMA range."

    return "Unknown event"


async def _save_detection_record(
    agent, event, forecast_prob: float, cluster_label: str
) -> None:
    """Saves the pedestrian detection event to the persistent database.

    Args:
        agent: The controller agent instance.
        event: The DetectionEvent instance.
        forecast_prob: The forecast zone occupancy probability.
    """
    event_data = {
        "timestamp": event.timestamp,
        "zone": event.zone,
        "pedestrians": event.pedestrians,
        "ema": event.ema,
        "cluster_label": cluster_label,
        "trend_label": event.event_type.value,
        "zone_occupancy_forecast": forecast_prob,
        "delta": event.pedestrians - event.ema,
    }
    if hasattr(agent, "call_tool"):
        await agent.call_tool("database-mcp", "save_detection_event", event_data)
    else:
        save_detection_event(event_data)


def _compute_brightness_and_decision(
    event, zone_plan: dict
) -> tuple[float, DecisionEvent]:
    """Calculates actuation brightness and creates a DecisionEvent.

    Args:
        event: The DetectionEvent instance.
        zone_plan: The planning dictionary containing forecast probability and brightness plan.

    Returns:
        A tuple of (brightness_to_lamp, decision_event).
    """
    brightness = event.new_brightness
    plan_brightness = zone_plan["brightness"]
    forecast_prob = zone_plan["prob dist"]

    brightness_to_lamp = (
        forecast_prob * plan_brightness + (1 - forecast_prob) * brightness
    )

    decision = DecisionEvent(
        eventid=event.eventid,
        zone=event.zone,
        event_type=event.event_type.value,
        brightness=brightness,
        reason=get_decision_reason(event.event_type, event.pedestrians),
        energy_saved_watts=calculate_energy_saved(brightness_to_lamp),
        timestamp=event.timestamp,
    )
    return brightness_to_lamp, decision


async def _save_decision_record(
    agent,
    event,
    decision: DecisionEvent,
    plan_brightness: float,
    brightness_to_lamp: float,
    cluster_label: str,
) -> None:
    """Saves the actuated brightness decision to the database.

    Args:
        agent: The controller agent instance.
        event: The DetectionEvent instance.
        decision: The DecisionEvent instance.
        plan_brightness: The predicted brightness from the planner.
        brightness_to_lamp: The final actuated brightness.
        cluster_label: The cluster label.
    """
    decision_data = {
        "timestamp": event.timestamp,
        "zone": decision.zone,
        "state": decision.event_type,
        "brightness": decision.brightness,
        "energy_saved_watts": decision.energy_saved_watts,
        "reason": decision.reason,
        "brightness_plan": plan_brightness,
        "reactive_brightness": decision.brightness,
        "brightness_to_lamp": brightness_to_lamp,
        "cluster_label": cluster_label,
    }
    if hasattr(agent, "call_tool"):
        await agent.call_tool("database-mcp", "save_decision_event", decision_data)
    else:
        save_decision_event(decision_data)


async def _apply_lamp_brightness(agent, brightness_to_lamp: float) -> None:
    """Sets the lamp brightness actuator to the calculated value.

    Args:
        agent: The controller agent instance.
        brightness_to_lamp: The brightness percentage to actuate.
    """
    if hasattr(agent, "call_tool"):
        await agent.call_tool(
            "controller-mcp",
            "set_lamp_brightness",
            {"percentage": int(brightness_to_lamp)},
        )
    else:
        from app.mcp.controller_service import set_lamp_brightness

        set_lamp_brightness(percentage=int(brightness_to_lamp))


async def run_luman_sense_loop(agent: ToolContext, iterations=30):
    """The background control loop that drives the Luman-Sense system.

    Loops through received events, calculates decision brightness values, and
    sets the lamp brightness.

    Args:
        agent: The controller agent instance driving this loop.
        iterations: Optional number of iterations to run (defaults to 30).
    """
    global centroids
    if not centroids:
        await get_traffic_clusters(agent)
    count = 0
    sum_energy_saved = 0
    sum_brightness = 0
    more_events = True

    # Maintain last decision and brightness level for each zone to prevent cross-zone leaks
    last_decisions = {}
    last_brightness_to_lamp = {}

    cluster_map = {
        0: "LOW_TRAFFIC",
        1: "CLEARING_TRAFFIC",
        2: "MODERATE_TRAFFIC",
        3: "TRAFFIC_SURGE",
        4: "PEAK_TRAFFIC",
    }

    for z in ["A", "B", "C", "D"]:
        last_decisions[z] = DecisionEvent(
            eventid=-1,
            zone=z,
            event_type="LOW_ACTIVITY",
            brightness=50,
            reason="initial state",
            energy_saved_watts=calculate_energy_saved(50),
            timestamp=datetime.now().strftime("%H:%M"),
        )
        last_brightness_to_lamp[z] = 50.0

    traffic_history = []
    while more_events:
        try:
            event = await event_queue.get()
            if not event:
                more_events = False
                break

            zone = event.zone
            zone_plan = brightness_plan.get(
                zone, {"zone": zone, "prob dist": 0.0, "brightness": 50}
            )
            forecast_prob = zone_plan["prob dist"]
            plan_brightness = zone_plan["brightness"]

            print("************")
            print(zone, event.pedestrians, event.ema)
            print(centroids[zone])
            print("************")
            if hasattr(agent, "call_tool"):
                cluster_id = await agent.call_tool(
                    "k-means-clusterer-mcp",
                    "predict",
                    {
                        "zone": zone,
                        "data": [[event.pedestrians, event.ema]],
                        "centroids": centroids[zone],
                    },
                )
                if isinstance(cluster_id, list):
                    cluster_id = cluster_id[0]
            else:
                from app.mcp.k_means_clusterer import predict as _predict

                cluster_ids = _predict(
                    zone, [[event.pedestrians, event.ema]], centroids[zone]
                )
                cluster_id = cluster_ids[0]

            cluster_label = cluster_map[cluster_id]
            print("cluster_label:", cluster_label)
            traffic_history.append(
                {
                    "cluster_id": cluster_id,
                    "zone": zone,
                    "pedestrians": event.pedestrians,
                    "ema": event.ema,
                }
            )

            # Save detection details
            await _save_detection_record(agent, event, forecast_prob, cluster_label)

            if event.flag:
                brightness_to_lamp, decision = _compute_brightness_and_decision(
                    event, zone_plan
                )
                last_decisions[zone] = decision
                last_brightness_to_lamp[zone] = brightness_to_lamp
                await _save_decision_record(
                    agent,
                    event,
                    decision,
                    plan_brightness,
                    brightness_to_lamp,
                    cluster_label,
                )
            else:
                decision = last_decisions[zone]
                brightness_to_lamp = last_brightness_to_lamp[zone]

        except Exception as e:
            import traceback

            traceback.print_exc()
            print(f"Action Error: {e}")
            decision = DecisionEvent(
                eventid=-1,
                zone="A",
                event_type="LOW_ACTIVITY",
                brightness=50,
                reason="error in event receipt",
                energy_saved_watts=calculate_energy_saved(50),
                timestamp=datetime.now().strftime("%H:%M"),
            )
            # Exit gracefully
            more_events = False
            continue

        # Set Actuator
        await _apply_lamp_brightness(agent, brightness_to_lamp)

        count += 1
        sum_energy_saved += decision.energy_saved_watts
        sum_brightness += decision.brightness
        if event:
            log(
                event,
                decision,
                count,
                plan_brightness,
                forecast_prob,
                brightness_to_lamp,
                event.ema,
                event.trend,
                event.delta,
            )

    print("[SUMMARY]")
    print(f"Total energy saved: {sum_energy_saved:.2f} W")
    avg_brightness = sum_brightness / count if count > 0 else 0.0
    print(f"Average brightness: {avg_brightness:.2f}")
    await fetch_analytics(agent)


def log(
    event,
    decision,
    count,
    plan_brightness,
    forecast_prob,
    brigtness_to_lamp,
    ema,
    trend,
    delta,
):
    """Logs the details of the input event and output decision parameters.

    Args:
        event: The input DetectionEvent.
        decision: The resulting DecisionEvent.
        count: The current iteration count.
        plan_brightness: The predicted brightness from the Markov plan.
        forecast_prob: The forecast transition probability.
        brigtness_to_lamp: The final calculated actuation brightness percentage.
        ema: The Exponential Moving Average of pedestrians.
        trend: The classified traffic trend.
        delta: The difference between current pedestrians and EMA.
    """
    print("\n[INPUT]")
    print(f" Zone              : {event.zone}")
    print(f" Pedestrians       : {event.pedestrians}")

    print("\n[ANALYTICS]")
    print(f" EMA               : {ema:.2f}")
    print(f" Trend             : {trend}")
    print(f" Delta             : {delta:.2f}")

    print("\n[PREDICTION]")
    print(f" Current Zone Forecast : {forecast_prob * 100:.2f}%")

    print("\n[STATE]")
    print(f" Event Type        : {event.event_type.value}")

    print("\n[REASON]")
    print(f" {decision.reason}")

    print("\n[CONTROL]")
    print(f" Predictive Brightness : {plan_brightness}%")
    print(f" Reactive Brightness   : {decision.brightness}%")
    print(f" Final Actuation       : {int(brigtness_to_lamp)}%")

    print("\n[ENERGY]")
    print(f" Estimated Energy Saved : {decision.energy_saved_watts:.2f} W")

    print("=" * 60)


async def discover_brightness_plan(agent: ToolContext = None):
    """Calculates future transition probabilities and updates global brightness_plan.

    Uses `plan_brightness_for_steps` to compute the expected brightness levels
    over the planning horizon for Zone A, initializing the predictive plan.
    """
    global brightness_plan
    print("═══════════════════════════════════════════════")
    print("LUMAN-SENSE EDGE AI INITIALIZATION")
    print("═══════════════════════════════════════════════")
    current_zone = "A"
    n_steps = 3

    # Try calling the sub-agent programmatically if a valid ToolContext is provided
    # and has the necessary session/invocation details.
    if agent is not None and hasattr(agent, "session") and agent.session is not None:
        from google.adk.tools import AgentTool

        try:
            planner_tool = AgentTool(brightness_planner_agent)
            result = await planner_tool.run_async(
                args={"current_zone": current_zone, "n_steps": n_steps},
                tool_context=agent,
            )
            # Reconstruct raw_plan_list from structured result
            raw_plan_list = []
            for plan in result.plans:
                plan_dict = plan.model_dump(by_alias=True)
                raw_plan_list.append({plan.zone: plan_dict})
        except Exception as e:
            print(
                f"[Warning] Failed to run sub-agent: {e}. Falling back to direct function call."
            )
            raw_plan_list = plan_brightness_for_steps(current_zone, n_steps)
    else:
        raw_plan_list = plan_brightness_for_steps(current_zone, n_steps)

    # Flatten the list of single-key dictionaries to a single flat dictionary
    brightness_plan = {}
    for item in raw_plan_list:
        for k, v in item.items():
            brightness_plan[k] = v

    print(f"[Markov] Current Zone: {current_zone}, Prediction hops {n_steps}")
    print("\n[PLANNER] Brightness Plan")
    print("-" * 45)
    print(f"{'Zone':<8}{'Forecast':<12}{'Brightness'}")
    print("-" * 45)

    for _zone, plan_details in brightness_plan.items():
        if hasattr(agent, "call_tool"):
            await agent.call_tool(
                "database-mcp",
                "save_footfall_predictions",
                zone=_zone,
                probability=plan_details["prob dist"],
                brightness=plan_details["brightness"],
            )
        else:
            from app.mcp.database_mcp import (
                save_footfall_predictions as _save_footfall_predictions,
            )

            _save_footfall_predictions(
                zone=_zone,
                probability=plan_details["prob dist"],
                brightness=plan_details["brightness"],
            )
        print(
            f"{plan_details['zone']:<8}{plan_details['prob dist']:<12.2f}{plan_details['brightness']}%"
        )

    print("-" * 45)
    print("[STATUS] Predictive lighting schedule established")


async def setup_database(agent: ToolContext):
    print("AGENT TYPE:", type(agent))
    print("AGENT DIR:", dir(agent))
    if hasattr(agent, "call_tool"):
        await agent.call_tool("database-mcp", "setup_database")
    else:
        _setup_database()
    print("[STATUS] Database setup complete")


async def fetch_analytics(agent: ToolContext = None):
    if hasattr(agent, "call_tool"):
        await agent.call_tool("database-mcp", "fetch_analytics")
    else:
        from app.mcp.database_mcp import fetch_analytics as _fetch_analytics

        _fetch_analytics()


async def get_traffic_clusters(agent: ToolContext = None):
    global cluster_discovery_map
    global centroids
    if hasattr(agent, "call_tool"):
        cluster_discovery_map, centroids = await agent.call_tool(
            "k-means-clusterer-mcp", "get_traffic_clusters"
        )
    else:
        from app.mcp.k_means_clusterer import (
            get_traffic_clusters as _get_traffic_clusters,
        )

        cluster_discovery_map, centroids = _get_traffic_clusters()
    return cluster_discovery_map, centroids


controller_agent = Agent(
    name="controller_agent",
    model=Gemini(model="gemini-3.1-flash-lite"),
    instruction="""
    You are the LumanSense Automated Dimming Controller.
    You initialize the telemetry database, discover the zone-wise predictive brightness plans, and run the real-time sensor processing loop.
    You process incoming pedestrian detection events from vision sensors and actuate street-lighting brightness levels to optimize energy footprint.
    """,
    tools=[setup_database, discover_brightness_plan, run_luman_sense_loop],
    sub_agents=[brightness_planner_agent],
)
