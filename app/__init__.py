"""Agent package.

This package defines the specialized agents (Orchestrator, Controller, Brightness Planner, Ask luman)
used by the LumanSense control loop and analytical user interface.
"""

from __future__ import annotations


def __getattr__(name: str):
    if name == "app":
        from app.agent.orchestrator_agent import app

        return app
    if name == "ask_luman_agent":
        from app.agent.ask_luman_agent import ask_luman_agent

        return ask_luman_agent
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["app", "ask_luman_agent"]
