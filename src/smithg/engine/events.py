from dataclasses import dataclass

from smithg.datatypes import Amount, Price, Item, CommandCost


@dataclass
class Event:
    @property
    def event_name(self) -> str:
        return self.__class__.__name__


@dataclass
class CommandCostReceipt(Event):
    command_cost_diff: CommandCost


@dataclass
class ItemTransfer(Event):
    item: Item
    amount: Amount


@dataclass
class MoneyTransfer(Event):
    amount: Amount


@dataclass
class TradeReceipt(Event):
    item: Item
    amount: Amount
    price: Price


@dataclass
class BuyReceipt(TradeReceipt):
    pass


@dataclass
class SellReceipt(TradeReceipt):
    pass
