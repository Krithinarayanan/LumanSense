"""Controller agent module.

This module defines the LumanSense Controller Agent, which manages real-time light
brightness adjustments based on detected motion events and hysteresis rules.
"""

from datetime import datetime

from google.adk import Agent
from google.adk.models import Gemini

from app.agent.brightness_planner_agent import plan_brightness_for_steps
from app.events.decision_event import DecisionEvent
from app.events.event_bus import event_queue
from app.events.event_types import EventType
from app.mcp.database_mcp import save_decision_event, save_detection_event
from app.mcp.database_mcp import setup_database as _setup_database
from app.mcp.energy_service import calculate_energy_saved

brightness_plan = {}
linear_models = {}


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


async def _save_detection_record(agent, event, forecast_prob: float) -> None:
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
        "cluster_label": event.cluster_label,
        "trend_label": event.event_type.value,
        "zone_occupancy_forecast": forecast_prob,
        "delta": event.pedestrians - event.ema,
    }
    if hasattr(agent, "call_tool"):
        await agent.call_tool("database-mcp", "save_detection_event", event_data)
    else:
        save_detection_event(event_data)


def _compute_brightness_and_decision(event, zone_plan: dict) -> tuple[float, DecisionEvent]:
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
) -> None:
    """Saves the actuated brightness decision to the database.

    Args:
        agent: The controller agent instance.
        event: The DetectionEvent instance.
        decision: The DecisionEvent instance.
        plan_brightness: The predicted brightness from the planner.
        brightness_to_lamp: The final actuated brightness.
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


async def run_luman_sense_loop(agent, iterations=30):
    """The background control loop that drives the Luman-Sense system.

    Loops through received events, calculates decision brightness values, and
    sets the lamp brightness.

    Args:
        agent: The controller agent instance driving this loop.
        iterations: Optional number of iterations to run (defaults to 30).
    """
    count = 0
    sum_energy_saved = 0
    sum_brightness = 0
    more_events = True

    # Initialize variables to safely persist state across iterations
    brightness_to_lamp = 50.0
    plan_brightness = 50
    decision = DecisionEvent(
        eventid=-1,
        zone="A",
        event_type="LOW_ACTIVITY",
        brightness=50,
        reason="initial state",
        energy_saved_watts=calculate_energy_saved(50),
        timestamp=datetime.now().strftime("%H:%M"),
    )

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

            # Save detection details
            await _save_detection_record(agent, event, forecast_prob)

            if event.flag:
                plan_brightness = zone_plan["brightness"]
                brightness_to_lamp, decision = _compute_brightness_and_decision(event, zone_plan)
                await _save_decision_record(agent, event, decision, plan_brightness, brightness_to_lamp)

        except Exception as e:
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
    fetch_analytics(agent)


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


def discover_brightness_plan():
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
        print(
            f"{plan_details['zone']:<8}{plan_details['prob dist']:<12.2f}{plan_details['brightness']}%"
        )

    print("-" * 45)
    print("[STATUS] Predictive lighting schedule established")


def fit_footfall_line_for_zones(agent):
    """Fits a linear regression model to pedestrian footfall data for Zone A."""
    global linear_models
    if hasattr(agent, "call_tool"):
        linear_models = agent.call_tool(
            "linear-regression-mcp", "build_fit_line_for_all_zones"
        )
    else:
        from app.mcp.linear_regression import build_fit_line_for_all_zones

        linear_models = build_fit_line_for_all_zones()

    print("\n[LINEAR REGRESSION MODEL]")
    print("-" * 45)
    for _zone, model in linear_models.items():
        print(
            f"Zone: {_zone} : Slope: {model['slope']:.2f} | Intercept: {model['intercept']:.2f} | MSE: {model['mse']:.2f}"
        )
    print("-" * 45)
    print("[STATUS] Linear regression model established")


def calculate_brightness_for_zones(agent, zone_pedestrians: dict[str, int]):
    """Calculates brightness levels for all zones based on pedestrian counts."""
    global brightness_plan
    global linear_models
    BRIGHTNESS_ZONES = ["A", "B", "C", "D"]
    for _zone in BRIGHTNESS_ZONES:
        if _zone not in brightness_plan:
            brightness_plan[_zone] = {
                "zone": _zone,
                "prob dist": 0.0,
                "brightness": 50,
            }

    for _zone, model in linear_models.items():
        pedestrians = zone_pedestrians.get(_zone, 0)
        brightness = model["slope"] * pedestrians + model["intercept"]
        brightness = max(0, min(100, brightness))
        brightness_plan[_zone]["brightness"] = brightness

    print("\n[BRIGHTNESS] Brightness Levels")
    print("-" * 45)
    print(f"{'Zone':<8}{'Brightness'}")
    print("-" * 45)
    for _zone, brightness in brightness_plan.items():
        print(f"{_zone:<8}{brightness['brightness']}%")
    print("-" * 45)
    print("[STATUS] Brightness levels established")


def setup_database(agent):
    if hasattr(agent, "call_tool"):
        agent.call_tool("database-mcp", "setup_database")
    else:
        _setup_database()
    print("[STATUS] Database setup complete")


def fetch_analytics(agent=None):
    if hasattr(agent, "call_tool"):
        agent.call_tool("database-mcp", "fetch_analytics")
    else:
        from app.mcp.database_mcp import fetch_analytics as _fetch_analytics

        _fetch_analytics()


controller_agent = Agent(
    name="controller_agent",
    model=Gemini(model="gemini-3.1-flash-lite"),
    instruction="""
    ### Agent Definition:
    You are the Luman-Sense Controller Agent.
    You have to initialize database using setup_database tool.
    Then, you discover the brightness plan using discover_brightness_plan tool at the beginning.
    You take current state and decide hysteresis-based brightness levels for all zones.
    You will need to loop through run_luman_sense_loop.
    You are responsible for listening to events from the vision module and updating
    brightness levels accordingly.
    """,
    tools=[
        setup_database,
        discover_brightness_plan,
        run_luman_sense_loop
    ],
)
