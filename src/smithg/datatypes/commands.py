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
    max_price: Price


@dataclass
class SellItem(_MakeTrade):
    min_price: Price


@dataclass
class Work(Command):
    amount: Amount

    @property
    def cost(self) -> CommandCost:
        return self.amount
