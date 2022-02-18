"""
This file implements a simple agent using the class model. You can write an agent yourself
by copying this file and change the implementations of the process and/or process_event
methods.
Make sure you keep the @smithg.register_agent_class decorator to teach smithg about your
agent class.
"""
from dataclasses import dataclass, field
import random
import logging

import smithg
from smithg import Agent, Environment, commands, events

_logger = logging.getLogger(__name__)
_logger.debug("Loading %s", __name__)

# The register_agent_class decorator instantiates the class for you
# and registers the agent with the canonical world.
@smithg.register_agent_class
@dataclass
class RandomAgent(Agent):
    rand: random.Random = field(default_factory=random.Random)

    def process(self, env: Environment) -> None:
        """
        Implement a random agent.

        Just pick some possible actions, like buying or selling an item.
        If no viable trade command can be found, just work to get some money.
        """
        _logger.debug("RandomAgent: processing")

        possible_commands: list[commands.Command] = []

        for buy in env.buy_offers:
            if env.inventory[buy.item] > 0:
                possible_commands.append(
                    commands.SellItem(
                        item=buy.item,
                        max_amount=env.inventory[buy.item],
                        min_price=buy.price,
                    )
                )

        for sell in env.sell_offers:
            max_amount = env.balance // sell.price
            if max_amount > 0:
                possible_commands.append(
                    commands.BuyItem(
                        item=sell.item, max_amount=max_amount, max_price=sell.price
                    )
                )

        if not possible_commands:
            possible_commands = [commands.Work(self.rand.randint(1, env.command_fuel))]

        self.safe_queue_command(env, self.rand.choice(possible_commands))
