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

# Decorator to register a function/class to the canonical world
def register_agent(name: str) -> Callable[[AgentFunc], AgentFunc]:
    def registrar(func: AgentFunc) -> AgentFunc:
        _logger.debug("Loading agent %s - %s", name, func)
        _canonical_world.register_agent(func, name)
        return func

    return registrar


def register_agent_class(cls):
    _logger.debug("Loading agent class %s", cls.__name__)
    agent = cls()
    _canonical_world.register_agent(agent, cls.__name__)
    return cls


simulate = _canonical_world.simulate
