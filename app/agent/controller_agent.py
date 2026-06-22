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
from app.mcp.energy_service import calculate_energy_saved

brightness_plan = {}


def get_decision_reason(event_type: EventType) -> str:
    """Returns a user-friendly description of the reasons leading to the decision.

    Args:
        event_type: The Type of event processed.

    Returns:
        A string explaining the decision reason.
    """
    if event_type == EventType.PEDESTRIAN_SPIKE:
        return "Pedestrian count exceeded activation threshold"

    if event_type == EventType.LOW_ACTIVITY:
        return "Traffic dropped below hysteresis release threshold"

    return "Unknown event"


async def run_luman_sense_loop(agent, iterations=30):
    """The background control loop that drives the Luman-Sense system."""
    count = 0
    sum_energy_saved = 0
    sum_brightness = 0
    moreEvents = True
    while moreEvents:
        try:
            event = await event_queue.get()
            if event:
                zone = event.zone
                brightness = event.new_brightness
                decision = DecisionEvent(
                    eventid=event.eventid,
                    zone=zone,
                    event_type=event.event_type.value,
                    brightness=brightness,
                    reason=get_decision_reason(event.event_type),
                    energy_saved_watts=calculate_energy_saved(brightness),
                    timestamp=datetime.now(),
                )
            else:
                moreEvents = False
                continue
        except Exception as e:
            print(f"Action Error: {e}")
            decision = DecisionEvent(
                eventid=-1,
                zone="A",
                event_type="LOW_ACTIVITY",
                brightness=50,
                reason="error in event receipt",
                energy_saved_watts=calculate_energy_saved(50),
                timestamp=datetime.now(),
            )
            # exit gracefully
            moreEvents = False
            continue

        zone_plan = brightness_plan.get(
            zone, {"zone": zone, "prob dist": 0.0, "brightness": 50}
        )
        plan_brightness = zone_plan["brightness"]
        forecast_prob = zone_plan["prob dist"]

        brigtness_to_lamp = max(decision.brightness, plan_brightness)

        if hasattr(agent, "call_tool"):
            await agent.call_tool(
                "controller-mcp",
                "set_lamp_brightness",
                {"percentage": brigtness_to_lamp},
            )
        else:
            from app.mcp.controller_service import set_lamp_brightness

            set_lamp_brightness(percentage=brigtness_to_lamp)
        count = count + 1
        sum_energy_saved += decision.energy_saved_watts
        sum_brightness += decision.brightness
        if event:
            log(
                event,
                decision,
                count,
                plan_brightness,
                forecast_prob,
                brigtness_to_lamp,
            )

    print("[SUMMARY]")
    print(f"Total energy saved: {sum_energy_saved}")
    print(f"Average brightness: {sum_brightness / count}")


def log(event, decision, count, plan_brightness, forecast_prob, brigtness_to_lamp):
    print("\n[INPUT]")
    print(f" Zone              : {event.zone}")
    print(f" Pedestrians       : {event.pedestrians}")

    print("\n[PREDICTION]")
    print(f" Current Zone Forecast : {forecast_prob * 100:.2f}%")

    print("\n[STATE]")
    print(f" Event Type        : {event.event_type.value}")

    print("\n[REASON]")
    print(f" {decision.reason}")

    print("\n[CONTROL]")
    print(f" Markov Prediction : {plan_brightness}%")
    print(f" Hysteresis Output : {decision.brightness}%")
    print(f" Final Actuation   : {brigtness_to_lamp}%")
    if decision.brightness < plan_brightness:
        print("\n[OVERRIDE]")
        print(" Predictive lighting activated")

    print("\n[ENERGY]")
    print(f" Estimated Energy Saved : {decision.energy_saved_watts} W")

    print("=" * 60)


def discover_brightness_plan():
    """Calculates future transition probabilities and updates global brightness_plan."""
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


controller_agent = Agent(
    name="controller_agent",
    model=Gemini(model="gemini-3.1-flash-lite"),
    instruction="""
    ### Agent Definition:
    You are the Luman-Sense Controller Agent.
    Discover the brightness plan using discover_brightness_plan tool at the beginning.
    You take current state and decide hysteresis-based brightness levels for all zones.
    You will need to loop through run_luman_sense_loop.
    You are responsible for listening to events from the vision module and updating
    brightness levels accordingly.
    """,
    tools=[discover_brightness_plan, run_luman_sense_loop],
)
