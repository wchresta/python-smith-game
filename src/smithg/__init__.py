from smithg.agents import Agent, Environment
from smithg.datatypes.datatypes import *
import smithg.datatypes.commands as commands
import smithg.datatypes.events as events
import smithg.engine

# Convenienve shortcuts
register_agent_func = smithg.engine.register_agent_func
register_agent_class = smithg.engine.register_agent_class

# Convenience types
CommandList = list[commands.Command]
EventList = list[events.Event]
