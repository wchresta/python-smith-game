from typing import NamedTuple
import dataclasses
from dataclasses import dataclass

Item = str
Amount = int
Price = int
CommandCost = Price


class TradeOffer(NamedTuple):
    item: Item
    amount: Amount
    price: Price


class BuyOffer(TradeOffer):
    @classmethod
    def from_trade(cls, trade: TradeOffer) -> "BuyOffer":
        return cls(*trade)

    def __repr__(self):
        return f"SELL({self.amount} {self.item} @ {self.price/100:0.2f})"


class SellOffer(TradeOffer):
    @classmethod
    def from_trade(cls, trade: TradeOffer) -> "SellOffer":
        return cls(*trade)

    def __repr__(self):
        return f"SELL({self.amount} {self.item} @ {self.price/100:0.2f})"
