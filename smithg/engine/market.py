from typing import Optional, Iterable, Callable
from dataclasses import dataclass, field

import collections
import random

from smithg.datatypes import Item, Amount, Price, BuyOffer, SellOffer, TradeOffer


@dataclass
class Trades:
    buys: dict[Item, BuyOffer] = field(default_factory=dict)
    sells: dict[Item, SellOffer] = field(default_factory=dict)

    def find_buy(self, item: Item) -> Optional[BuyOffer]:
        try:
            return self.buys[item]
        except KeyError:
            return None

    def find_sell(self, item: Item) -> Optional[SellOffer]:
        try:
            return self.sells[item]
        except KeyError:
            return None

    def buy_offer_set(self) -> frozenset[BuyOffer]:
        return frozenset(BuyOffer(*b) for b in self.buys.values())

    def sell_offer_set(self) -> frozenset[SellOffer]:
        return frozenset(SellOffer(*s) for s in self.sells.values())


@dataclass
class Market:
    trades: Trades = field(default_factory=Trades)

    def tick(self) -> None:
        pass


@dataclass
class RandomMarket(Market):
    rand: random.Random = field(default_factory=random.Random)
    known_items: list[Item] = field(default_factory=list)
    item_distributions: dict[Item, tuple[Callable[[], Amount], Callable[[], Price]]] = field(default_factory=dict)

    def __post_init__(self):
        for item in self.known_items:
            mid_price = self.rand.randint(2, 9999)
            mid_amount = self.rand.randint(-999, 999)
            self.item_distributions[item] = (
                lambda: int(self.rand.triangular(1, 10000, mid_price)),
                lambda: int(self.rand.triangular(-1000, 1000, mid_amount)),
            )

    def tick(self) -> None:
        self.trades.buys.clear()
        self.trades.sells.clear()

        for item, distrs in self.item_distributions.items():
            price = distrs[0]()
            amount = distrs[1]()

            if amount < 0:
                # Selling
                self.trades.sells[item] = SellOffer(item=item, amount=-amount, price=price)
            elif amount > 0:
                self.trades.buys[item] = BuyOffer(item=item, amount=amount, price=price)
