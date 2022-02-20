from dataclasses import dataclass, field
from typing import Iterable, Callable
import logging
import collections

from smithg.agents import AgentFunc, Environment, Registry, global_agent_registry
from smithg.datatypes import Item, Amount, BuyOffer, SellOffer, events, commands
from smithg.engine import market as engine_market

_logger = logging.getLogger(__name__)


@dataclass(slots=True, frozen=True)  # type: ignore
class AgentContainer:
    @dataclass
    class State:
        command_fuel: int = 0
        balance: Amount = 0
        items: dict[Item, Amount] = field(
            default_factory=lambda: collections.defaultdict(int)
        )

    agent_func: AgentFunc
    agent_name: str
    state: "AgentContainer.State" = field(default_factory=State)
    events_queue: list[events.Event] = field(default_factory=list)

    balance_increase: Amount = 0
    command_fuel_increase: Amount = 25  # Fuel generation every round
    work_to_money: int = 1


@dataclass
class World:
    known_items: list[Item]
    market: engine_market.Market = field(default_factory=engine_market.Market)
    player_agent_containers: list[AgentContainer] = field(default_factory=list)

    work_to_money: int = 10
    balance_init: Amount = 100
    balance_increase: Amount = 0
    command_fuel_init: Amount = 100
    command_fuel_increase: Amount = 25

    def add_agents_from_registry(self, registry: Registry) -> None:
        for agent_func, name in registry.agents:
            self.add_agent(agent_func, name)

    def add_agent(self, agent_func: AgentFunc, name: str = None) -> None:
        if not name:
            name = agent_func.__name__

        self.player_agent_containers.append(
            AgentContainer(
                agent_func=agent_func,
                agent_name=name,
                state=AgentContainer.State(
                    command_fuel=self.command_fuel_init, balance=self.balance_init
                ),
                command_fuel_increase=self.command_fuel_increase,
                balance_increase=self.balance_increase,
                work_to_money=self.work_to_money,
            )
        )

    # Simulate a run with the given number of steps
    def simulate(self, steps=1000) -> list[AgentContainer]:
        for s in range(steps):
            self.step(s)

        return self.player_agent_containers

    def process_step(self) -> None:
        self.market.tick()

    def step(self, s: int) -> None:
        self.process_step()

        for cont in self.player_agent_containers:
            execute_agent(cont, self)


def make_world(
    known_items: Iterable[str],
    player_agents: Iterable[tuple[AgentFunc, str]] = None,
    agent_registry: Registry = global_agent_registry,
) -> World:
    if not player_agents:
        player_agents = []

    known_items = list(known_items)
    world = World(
        known_items=known_items,
        market=engine_market.RandomMarket(known_items=known_items),
    )

    world.add_agents_from_registry(agent_registry)

    for agent, name in player_agents:
        world.add_agent(agent, name)

    return world


def execute_agent(cont: AgentContainer, world: World) -> None:
    # Create some fuel for new commands
    cont.state.command_fuel += cont.command_fuel_increase
    cont.state.balance += cont.balance_increase

    # Tell the agent about its environment.
    env = Environment(
        known_items=frozenset(world.known_items),
        buy_offers=world.market.trades.buy_offer_set(),
        sell_offers=world.market.trades.sell_offer_set(),
        balance=cont.state.balance,
        command_fuel=cont.state.command_fuel,
        inventory=collections.defaultdict(
            int, {item: amount for item, amount in cont.state.items.items()}
        ),
    )

    _logger.debug("Calling agent with events: %s", cont.events_queue)
    queued_commands = cont.agent_func(env, cont.events_queue)  # type: ignore # https://github.com/python/mypy/issues/5485
    _logger.debug("Agent finished and is executing commands %s", queued_commands)

    if not isinstance(queued_commands, list):
        raise InvalidAgentState(
            f"Returned command list is not a list. Found {type(queued_commands)}"
        )
    cont.events_queue.clear()

    for cmd in queued_commands:
        if not isinstance(cmd, commands.Command):
            raise InvalidAgentState(
                f"Returned command is not a subclass of Command. Found {type(cmd)}"
            )

        # TODO: Make sure the command is of a subclass within commands and not something fishy the agent gave us
        execute_command(cont, world, cmd)


def execute_command(cont: AgentContainer, world: World, cmd: commands.Command) -> None:
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


class InvalidAgentState(RuntimeError):
    pass
