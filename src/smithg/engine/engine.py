from dataclasses import dataclass, field
from typing import Iterable
import logging
import collections

from smithg.agents import agents, commands
from smithg.datatypes import Item, Amount, BuyOffer, SellOffer
from smithg.engine import market, events

_logger = logging.getLogger(__name__)


@dataclass
class AgentContainer:
    @dataclass
    class State:
        command_fuel: int = 0
        last_command_fuel: int = 0
        last_balance: Amount = 0
        balance: Amount = 0
        last_items: dict[Item, Amount] = field(
            default_factory=lambda: collections.defaultdict(int)
        )
        items: dict[Item, Amount] = field(
            default_factory=lambda: collections.defaultdict(int)
        )

    agent_func: agents.AgentFunc
    state: "AgentContainer.State" = field(default_factory=State)
    command_fuel_generation: int = 25  # Fuel generation every round
    events_queue: list[events.Event] = field(default_factory=list)
    work_to_money: int = 1


@dataclass
class World:
    known_items: list[Item]
    market: market.Market
    player_agent_containers: list[AgentContainer]


def setup_world(player_agents: Iterable[agents.AgentFunc]):
    known_items = [
        "iron_ore",
        "iron_ingot",
        "iron_sword",
        "iron_sheets",
        "iron_hammer",
    ]
    world = World(
        known_items=known_items,
        market=market.Market(trades=market.gen_random_trade_offers(known_items)),
        player_agent_containers=list(
            AgentContainer(
                a, state=AgentContainer.State(command_fuel=100), work_to_money=10
            )
            for a in player_agents
        ),
    )
    return world


# Simulate a run with the given number of steps
def simulate(
    player_agents: Iterable[agents.AgentFunc] = None, steps=10
) -> list[AgentContainer]:
    if not player_agents:
        player_agents = []

    world = setup_world(player_agents)

    for s in range(steps):
        step(world, s)

    return world.player_agent_containers


class InvalidAgentState(RuntimeError):
    pass


def execute_command(world: World, cont: AgentContainer, cmd: commands.Command) -> None:
    cont.state.command_fuel -= cmd.cost
    if cont.state.command_fuel < 0:
        raise InvalidAgentState(f"Agent ran out of fuel with command {cmd}")

    if isinstance(cmd, commands.Work):
        # Fuel has already been paid. Now it's payday!
        cont.state.balance += cont.work_to_money * cmd.cost
    if isinstance(cmd, commands.BuyItem):
        # Check if the world has an open SellOffer for this buy
        item = cmd.item
        if item not in world.known_items:
            raise InvalidAgentState(
                f"Agent provided invalid buy command for non-existent item {item}"
            )

        sell = world.market.trades.find_sell(item)
        if not sell:
            _logger.info("Agent tried to buy an item that is not for sale.")
            return
        if sell.price > cmd.max_price:
            _logger.info("Agent is not willing to pay that is necessary to buy.")
            return
        # Agent can buy
        bought_amount = min(sell.amount, cmd.max_amount)
        total_price = bought_amount * sell.price
        cont.state.balance -= total_price
        cont.state.items[item] += bought_amount

        cont.events_queue.append(events.BuyReceipt(item, bought_amount, sell.price))
        _logger.info(f"Agent bought {bought_amount} of {item} at {sell.price}")
        return
    if isinstance(cmd, commands.SellItem):
        # Check if the world has an open BuyOffer for this buy
        item = cmd.item
        if item not in world.known_items:
            raise InvalidAgentState(
                f"Agent provided invalid buy command for non-existent item {item}"
            )

        buy = world.market.trades.find_buy(item)
        if not buy:
            _logger.info("Agent tried to sell an item that nobody is buying.")
            return
        if buy.price < cmd.min_price:
            _logger.info(
                "Agent is not willing to sell for the price that the item is wanted for."
            )
            return
        # Agent can sell
        bought_amount = min(buy.amount, cmd.max_amount)
        if bought_amount > cont.state.items[item]:
            raise InvalidAgentState(f"Agent is trying to sell more {item} thatn it has")
        total_price = bought_amount * buy.price
        cont.state.balance += total_price
        cont.state.items[item] -= bought_amount

        cont.events_queue.append(events.SellReceipt(item, bought_amount, buy.price))
        _logger.info(f"Agent sold {bought_amount} of {item} at {buy.price}")
        return


def execute_agent(world: World, cont: AgentContainer) -> None:
    env = agents.Environment(
        known_items=frozenset(world.known_items),
        buy_offers=world.market.trades.buy_offer_set(),
        sell_offers=world.market.trades.sell_offer_set(),
    )

    # Create some fuel for new commands
    cont.state.command_fuel += cont.command_fuel_generation

    sync_events = create_sync_events(cont)

    # We always want to make the command cost receipt come first
    cont.events_queue = sync_events + cont.events_queue

    _logger.debug("Calling agent with events: %s", cont.events_queue)
    queued_commands = cont.agent_func(env, cont.events_queue)
    _logger.debug("Agent finished and is executing commands %s", queued_commands)

    if not isinstance(queued_commands, list):
        raise InvalidAgentState(
            f"Returned command list is not a list. Found {type(queued_commands)}"
        )
    cont.events_queue = []

    for cmd in queued_commands:
        if not isinstance(cmd, commands.Command):
            raise InvalidAgentState(
                f"Returned command is not a subclass of Command. Found {type(cmd)}"
            )

        # TODO: Make sure the command is of a subclass within commands and not something fishy the agent gave us
        execute_command(world, cont, cmd)


def create_sync_events(cont: AgentContainer) -> list[events.Event]:
    sync_events: list[events.Event] = []

    diff_command_fuel = cont.state.command_fuel - cont.state.last_command_fuel
    cont.state.last_command_fuel = cont.state.command_fuel
    if diff_command_fuel != 0:
        sync_events.append(events.CommandCostReceipt(diff_command_fuel))

    diff_balance = cont.state.balance - cont.state.last_balance
    cont.state.last_balance = cont.state.balance
    if diff_balance != 0:
        sync_events.append(events.MoneyTransfer(diff_balance))

    for item, amount in cont.state.items.items():
        diff_amount = amount - cont.state.last_items[item]
        cont.state.last_items[item] = amount
        if diff_amount != 0:
            sync_events.append(events.ItemTransfer(item, diff_amount))

    return sync_events


def step(world: World, s: int) -> None:
    world.market.trades = market.gen_random_trade_offers(world.known_items)

    for cont in world.player_agent_containers:
        execute_agent(world, cont)
