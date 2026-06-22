import asyncio

from google.adk.apps import App
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

import app
from app.agent.orchestrator_agent import orchestrator_agent
from app.camera_feed.yolo_mock import yolo_mock_producer

app = App(  # noqa: F811
    root_agent=orchestrator_agent,
    name="app",
)


# --- Execution Setup ---
async def main():
    # 1. Start the yolo mock producer in the background
    background_tasks = set()
    producer_task = asyncio.create_task(yolo_mock_producer())
    background_tasks.add(producer_task)
    producer_task.add_done_callback(background_tasks.discard)

    # 2. Initialize an in-memory session service to track conversation state
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name="app", user_id="user", session_id="s1"
    )

    # 3. Initialize the Runner with your app and session service
    runner = Runner(app=app, session_service=session_service)

    # 4. Start the agent/app execution
    print("Starting LumanSense Orchestrator...")

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
                print(f"[{event.author}]: {text}")


if __name__ == "__main__":
    # Execute the async main function
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nLumanSense stopped by user.")
