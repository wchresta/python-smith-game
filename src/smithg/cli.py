import importlib
import pathlib

import smithg.engine
import smithg.agents

import logging

_logger = logging.getLogger(__name__)


def discover_agents(agents_package: str) -> None:
    for agentfile in pathlib.Path(agents_package).glob("*.py"):
        module_name = f"{agents_package}.{agentfile.stem}"
        _logger.debug("Importing %s", module_name)
        importlib.import_module(module_name, package=None)


def main():
    logging.basicConfig(level=logging.INFO)

    agents_path = "player_agents"
    _logger.info("Loading agents from %s", agents_path)
    discover_agents(agents_path)
    _logger.info("Loading done.")

    _logger.info("Running simulation...")
    agent_container = smithg.engine.simulate()

    _logger.info("Simulation finished. Here are the results")
    for cont in sorted(agent_container, key=lambda x: x.state.balance, reverse=True):
        _logger.info("Agent %s, balance: %i", cont.agent_name, cont.state.balance)


if __name__ == "__main__":
    main()
