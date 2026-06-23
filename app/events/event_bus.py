"""Asynchronous event queue for LumanSense event routing.

This module provides the global asynchronous event queue (`event_queue`) used to
pass events from vision processing modules/sensors to controller agents.
"""

import asyncio

event_queue = asyncio.Queue()
