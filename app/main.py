"""Main entry point for the LumanSense system.

This script initializes the environmental coordinator and executes the automated
dimming control loop, driving real-time municipal street-lighting actuation based on
simulated pedestrian flow telemetry.
"""

import asyncio
import logging

from google.adk.apps import App
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

import app
from app.agent.orchestrator_agent import orchestrator_agent
from app.camera_feed.yolo_mock import yolo_mock_producer

logger = logging.getLogger("luman_sense")

app = App(  # noqa: F811
    root_agent=orchestrator_agent,
    name="app",
)


async def main():
    """Starts the simulated pedestrian flow telemetry feed and runs the automated control coordinator.

    This function coordinates the background simulation of pedestrian traffic and the
    asynchronous execution loop of the central environmental controller.

    Raises:
        KeyboardInterrupt: If the execution is stopped by a user interrupt.
    """

    # Start the pedestrian telemetry feed simulation in the background
    background_tasks = set()
    producer_task = asyncio.create_task(yolo_mock_producer())
    background_tasks.add(producer_task)
    producer_task.add_done_callback(background_tasks.discard)

    # Initialize a session service to track state transitions
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name="app", user_id="user", session_id="s1"
    )

    # Initialize the runner to drive the automated lighting loop
    runner = Runner(app=app, session_service=session_service)

    # Start the control loop coordinator
    logger.info("Starting LumanSense Control Loop...")

    async for event in runner.run_async(
        user_id="user",
        session_id="s1",
        new_message=types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    text="Start the Luman-Sense system. Plan future brightness and run the control loop."
                )
            ],
        ),
    ):
        if event.content and event.content.parts:
            text = event.content.parts[0].text
            if text:
                logger.info("[%s]: %s", event.author, text)


if __name__ == "__main__":
    from app.logging_config import setup_logging
    setup_logging()
    # Execute the control loop
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nLumanSense stopped by user.")
