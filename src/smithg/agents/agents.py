"""
Agents are actors within the world which consume events and produce commands.

Agents are scored according to their
"""

from typing import Callable
import random
from dataclasses import dataclass, field
import collections
import logging

from smithg.datatypes import Item, Amount, BuyOffer, SellOffer, commands, events

_logger = logging.getLogger(__name__)


@dataclass(slots=True, frozen=True)  # type: ignore
class Environment:
    """
    Represent the environment the agent runs in.

    This can be used by agents to gain information about their own state, and about
    the state of the world. It contains information about the known items, sell and
    buy offers, and information about the agent state like balance, command_fuel
    and currently posessed items.

    known_items: A set of all item names that can be owned, bought or sold.
    buy_offers: A set of all known buy offers. Executed SellCommands with a matching
      buy offer in this set are guaranteed to be executed.
    sell_offers: A set of all known sell offers. Executed BuyCommands with a matching
      sell offer in this set are guaranteed to be executed.
    balance: Currently available funds. Can be used in BuyCommands.
    command_fuel: Currently avilable command fuel to execute commands.
    inventory: Dict of the agents inventory. It contains previously bought items.
      Note this is a defaultdict, so any item which is not posessed returns amount 0.
    """

    known_items: frozenset[Item]
    buy_offers: frozenset[BuyOffer]
    sell_offers: frozenset[SellOffer]
    balance: Amount
    command_fuel: Amount
    inventory: collections.defaultdict[Item, Amount]


AgentFunc = Callable[[Environment, list[events.Event]], list[commands.Command]]


@dataclass
class Agent:
    """
    An agent class that does nothing.

    This agent class implements some rudimentary infrastructure to be able to process
    events and enqueue commands. To make useful Agents, you should at least either
    override the process_event or the process method.

    The structure is as follows:
    * When the agent is called, self is initialized empty (any previous state within
      new_events or queued_commands is lost).
    * For every incoming events, self.process_event is called with the environment
      and the event. If the method returns False, the event is added to self.new_events
    * self.process is called with the environment. Not fully processed events can be
      accessed from self.new_events.
    * All commands added to self.commands are returned as the actions this Agents wants
      to execute. Note, that this agent does not check if actions are valid, including
      whether there is enough command fuel to execute the command.

    Other things to note:
    * Both the process_event and process methods can add commands to the command queue.
    * self.safe_queue_command can be used to safely enqueue commands, without risking
      to run out of fuel_commands. Note that this does not perform any other checks,
      like the existence of items on sell commands.

    Furthermore, keep in mind that this class is not necessary to implement an Agent.
    Agents are just callable with the AgentFunc signature. Functions with the correct
    signature can be used instead of this Agent class. This agent class implements
    __call__ which just calls self.run.
    """

    queued_commands: list[commands.Command] = field(default_factory=list)
    new_events: list[events.Event] = field(default_factory=list)

    def run(
        self, env: Environment, events: list[events.Event]
    ) -> list[commands.Command]:
        """
        Process an agent function call.

        This implements AgentFunc, which makes this class a valid Agent.
        For details on how Agent implements the Agent class and connects the rest of
        the methods, refer to the class docstring.
        """
        self.new_events = []
        self.queued_commands = []

        for evt in events:
            if not self.process_event(evt, env):
                self.new_events.append(evt)

        self.process(env)

        return self.queued_commands

    def queue_command(self, command: commands.Command) -> None:
        """Add the given command to the command queue. Do not perform any checks."""
        _logger.debug("Queued command %s", command)
        self.queued_commands.append(command)

    def safe_queue_command(self, env: Environment, command: commands.Command) -> bool:
        """
        Enqueue the given command if there is enough command fuel available.

        Returns true if enqueueing is successful, false otherwise.
        """
        if env.command_fuel < command.cost + sum(c.cost for c in self.queued_commands):
            _logger.debug("Ran out of fuel, cannot queue command %s", command)
            return False

        self.queue_command(command)
        return True

    def process_event(self, event: events.Event, env: Environment) -> bool:
        """
        Process an event and return if the event is fully processed.

        This is called by the run methdo on all incoming events. If this method returns
        true, the event is considered to be fully processed. If it returns false, the
        event is not fully processed and is added to self.new_events.

        The Agent base implementation does not process any event.
        """
        return False

    def process(self, env: Environment) -> None:
        """
        Perform agent logic.

        process is called _after_ events are processed by process_events, and _before_
        any commands are returned. This is a good place to implement functionality that
        needs visibility into more than one unprocessed event. Event-based logic should go
        into process_event.
        """
        pass

    def __call__(
        self, env: Environment, events: list[events.Event]
    ) -> list[commands.Command]:
        return self.run(env, events)


@dataclass
class Registry:
    agents: list[tuple[AgentFunc, str]] = field(default_factory=list)

    def register_agent(self, func: AgentFunc, name: str = None) -> None:
        if not name:
            name = func.__name__
        self.agents.append((func, name))

    def register_agent_func(self, name: str = None) -> Callable[[AgentFunc], AgentFunc]:
        def registrar(func: AgentFunc) -> AgentFunc:
            _logger.debug("Loading agent %s - %s", name, func)
            self.register_agent(func, name)
            return func

        return registrar

    def register_agent_class(self, cls):
        _logger.debug("Loading agent class %s", cls.__name__)
        agent = cls()
        self.register_agent(agent, cls.__name__)
        return cls


global_agent_registry = Registry()
