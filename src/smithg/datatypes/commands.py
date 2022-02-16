"""
The commands module provides the interfaces necessary to interact with the smith game.

Intead of executing commands directly, these interfaces are used to communicate intent.
"""
from dataclasses import dataclass
import abc

from smithg.datatypes.datatypes import Amount, Item, Price, CommandCost


class Command(abc.ABC):
    @property
    @abc.abstractmethod
    def cost(self) -> CommandCost:
        ...


@dataclass
class _MakeTrade(Command):
    item: Item
    max_amount: Amount

    @property
    def cost(self) -> CommandCost:
        return 50


@dataclass
class BuyItem(_MakeTrade):
    """
    Informs the world the agent wants to buy an item.

    item: The item the agent wants to buy. Must be in env.known_items
    max_amount: Maximal amount of items the agent wants to buy.
    max_price: The maximal price the agent is willing to pay.

    If max_amount * max_price is larger than the agents balance, there
    is a risk the agent will explode due to insufficient funds.

    Executing this command costs command fuel as given by .cost.
    """
    max_price: Price


@dataclass
class SellItem(_MakeTrade):
    """
    Informs the world the agent wants to buy an item.

    item: The item the agent wants to buy. Must be in env.known_items
    max_amount: Maximal amount of items the agent wants to buy.
    min_price: The minimal price the agent want to sell the item for.

    Executing this command costs command fuel as given by .cost.
    """
    min_price: Price


@dataclass
class Work(Command):
    """
    Converts `amount` of command fuel to money.

    The amont of money per command fuel depends on the simulation.

    Executing this command costs command fuel as given by .cost.
    """
    amount: Amount

    @property
    def cost(self) -> CommandCost:
        return self.amount
