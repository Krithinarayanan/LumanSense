"""Agent package.

This package defines the specialized agents (Orchestrator, Controller, Brightness Planner, Ask Lumen)
used by the LumanSense control loop and analytical user interface.
"""

from __future__ import annotations


def __getattr__(name: str):
    if name == "app":
        from .orchestrator_agent import app
        return app
    if name == "ask_lumen_agent":
        from .ask_lumen_agent import ask_lumen_agent
        return ask_lumen_agent
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["app", "ask_lumen_agent"]