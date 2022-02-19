from typing import Callable
import logging
import functools

from smithg.agents import global_agent_registry
from . import engine

_logger = logging.getLogger(__name__)


def simulate() -> list[engine.AgentContainer]:
    canonical_items = (
        "iron_ore",
        "iron_ingot",
        "iron_sword",
        "iron_sheets",
        "iron_hammer",
    )

    world = engine.make_world(canonical_items)
    return world.simulate()
