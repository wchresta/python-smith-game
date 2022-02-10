from typing import Optional, Literal
from dataclasses import dataclass

import collections
import random

from smithg.datatypes import Item, Amount, Price, BuyOffer, SellOffer, TradeOffer


@dataclass
class Trades:
    buys: dict[Item, BuyOffer]
    sells: dict[Item, SellOffer]

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
    trades: Trades


def gen_random_trade_offer(item: Item) -> TradeOffer:
    return TradeOffer(
        item=item,
        amount=random.randint(1, 100),
        price=random.randint(1, 10000),
    )


def gen_random_trade_offers(items: list[Item]) -> Trades:
    items = items[:]
    random.shuffle(items)
    mid_point = len(items) // 2
    buy_items, sell_items = items[:mid_point], items[mid_point:]

    TradeOffer("hello", 1, 1)

    return Trades(
        buys={
            item: BuyOffer.from_trade(gen_random_trade_offer(item))
            for item in buy_items
        },
        sells={
            item: SellOffer.from_trade(gen_random_trade_offer(item))
            for item in sell_items
        },
    )
