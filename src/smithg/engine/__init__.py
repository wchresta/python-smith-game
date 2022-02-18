from typing import Callable
import logging
import functools

from smithg.agents import AgentFunc
from . import engine

_logger = logging.getLogger(__name__)

_canonical_items = (
    "iron_ore",
    "iron_ingot",
    "iron_sword",
    "iron_sheets",
    "iron_hammer",
)
_canonical_world = engine.make_world(_canonical_items)

register_agent = _canonical_world.register_agent
register_agent_class = _canonical_world.register_agent_class
register_agent_func = _canonical_world.register_agent_func

simulate = _canonical_world.simulate
