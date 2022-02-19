# python-smith-game

**python-smith-game** is a Python library and infrastructure for a forging
themed coding game with trading elements. Players write programs that compete
with each other, instead of playing themselves.

## How to run the simulation

Download the project (we do not offer a Python package at the moment).
To test run the simulation for the first time, run the following command.

```bash
$ python src/smithg/cli.py
```

or when you installed the package, you can also use
```bash
$ smithg
```

This does the following:
* Read all agents from the `smithg.agents.examples` module. It includes a RandomAgent.
* Instantiate a world, and simulate it for a number of steps.
* When simulation finishes, print the results.

Winner is whichever agent has the most money at the end of the simulation.

## How to implement your own agent

Add a python script in the `player_agents/` directory in your current folder.
You can register your agents using the `smithg.register_agent_func` or
`smithg.register_agent_class` decorators. See the examples in
`smithg.agents.examples`. You can change the folder name by providing the
`--agents_dir` flag.

An agent is a callable of the form:

```python
smithg.Environment, smithg.EventList -> smithg.CommmandList
```

The environment contains information about the environment (duh!) and the agent
itself (like balance and inventory), and the events contain events like
receipts for successful item sells and buys.

Executing commands costs command fuel. The current available fuel can be seen
in `env.command_fuel`. The cost of a command can be seen in its command class
as `Command.cost`.

## World

The world is currently very minimalistic. It contains a few known items
which can be sold or bought (see the `Environment` docstring for details).

Commands the agent can perform are:

* BuyItem: Buy the given item.
* SellItem: Sell the given item.
* Work: Convert the given amount of command fuel to money.

## LICENSE
**python-smith-game** is licensed under the OSI approved
Apache License 2.0 (Apache-2.0). See the LICENSE file.
