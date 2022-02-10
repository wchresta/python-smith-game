from typing import Callable
import random
from dataclasses import dataclass, field
import collections
import logging

from smithg.agents import commands
from smithg.engine import events
from smithg.datatypes import Item, Amount, BuyOffer, SellOffer

_logger = logging.getLogger(__name__)


@dataclass(slots=True, frozen=True)
class Environment:
    known_items: frozenset[Item]
    buy_offers: frozenset[BuyOffer]
    sell_offers: frozenset[SellOffer]


AgentFunc = Callable[[Environment, list[events.Event]], list[commands.Command]]


@dataclass
class Agent:
    command_fuel: int = 0
    queued_commands: list[commands.Command] = field(default_factory=list)
    new_events: list[events.Event] = field(default_factory=list)

    class NotEnoughCommandFuel(RuntimeError):
        pass

    def process_event(self, evt: events.Event) -> bool:
        if isinstance(evt, events.CommandCostReceipt):
            self.command_fuel += evt.command_cost_diff
            assert self.command_fuel > 0
            return True
        return False

    def run(
        self, env: Environment, events: list[events.Event]
    ) -> list[commands.Command]:
        self.new_events = []
        self.queued_commands = []

        for evt in events:
            if not self.process_event(evt):
                self.new_events.append(evt)

        self.process(env)

        return self.queued_commands

    def queue_command(self, command: commands.Command) -> None:
        if self.command_fuel - command.cost < sum(c.cost for c in self.queued_commands):
            _logger.debug(
                "Ran out of fuel. Have proceesing power %i, but it costs %i",
                self.command_fuel,
                command.cost,
            )
            raise Agent.NotEnoughCommandFuel()

        _logger.debug("Queued command %s", command)
        self.queued_commands.append(command)

    def safe_queue_command(self, command: commands.Command) -> bool:
        try:
            self.queue_command(command)
            return True
        except Agent.NotEnoughCommandFuel:
            return False

    def process(self, env: Environment) -> None:
        pass

    @property
    def agent_func(self) -> AgentFunc:
        return self.run

    def __call__(
        self, env: Environment, events: list[events.Event]
    ) -> list[commands.Command]:
        return self.agent_func(env, events)


@dataclass
class InventoryAgent(Agent):
    balance: Amount = 0
    inventory: dict[Item, Amount] = field(
        default_factory=lambda: collections.defaultdict(Amount)
    )

    def process_event(self, evt: events.Event) -> bool:
        if isinstance(evt, events.ItemTransfer):
            self.inventory[evt.item] += evt.amount
            return True
        elif isinstance(evt, events.MoneyTransfer):
            self.balance += evt.amount
            return True
        return super().process_event(evt)


@dataclass
class RandomAgent(InventoryAgent):
    rand: random.Random = field(default_factory=random.Random)

    def process(self, env: Environment) -> None:
        _logger.debug("RandomAgent: processing")

        possible_commands: list[commands.Command] = []

        for buy in env.buy_offers:
            if self.inventory[buy.item] > 0:
                possible_commands.append(
                    commands.SellItem(
                        item=buy.item,
                        max_amount=self.inventory[buy.item],
                        min_price=buy.price,
                    )
                )

        for sell in env.sell_offers:
            max_amount = self.balance // sell.price
            if max_amount > 0:
                possible_commands.append(
                    commands.BuyItem(
                        item=sell.item, max_amount=max_amount, max_price=sell.price
                    )
                )

        if not possible_commands:
            possible_commands = [commands.Work(self.rand.randint(1, self.command_fuel))]

        self.safe_queue_command(self.rand.choice(possible_commands))
