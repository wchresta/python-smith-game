"""
This file uses the lower level AgentFunc model for agents, as opposed
to the class model. See the `random_agent.py` file to an example on
how to use the class model.

If you want to keep state in your AgentFunc, you'll nedd to create
a closure.
"""

import smithg


@smithg.register_agent_func("work_agent")
def work_agent(env: smithg.Environment, events: smithg.EventList) -> smithg.CommandList:
    """This agent does nothing but work."""
    return [smithg.commands.Work(amount=env.command_fuel)]
