from dataclasses import dataclass

from .datatypes import Amount, Price, Item, CommandCost


@dataclass
class Event:
    @property
    def event_name(self) -> str:
        return self.__class__.__name__


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
