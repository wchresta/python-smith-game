import argparse
import importlib
import pathlib
import sys
from typing import NamedTuple
import logging

import smithg
import smithg.engine
import smithg.agents


_logger = logging.getLogger(__name__)


def discover_agents(agents_package: str) -> None:
    _logger.debug("Discovering agents in %s", agents_package)
    for agentfile in pathlib.Path(agents_package).glob("*.py"):
        module_name = f"{agents_package}.{agentfile.stem}"
        _logger.debug("Importing %s", module_name)
        importlib.import_module(module_name, package=None)


class Result(NamedTuple):
    name: str
    score: int


def output_text(results: list[Result]):
    print("Simulation finished. Here are the results")
    for name, score in results:
        print(f"Agent {name:20} $ {score:8d}")


def output_json(results: list[Result]):
    import json

    print(json.dumps(results))


def output_csv(results: list[Result]):
    import csv

    writer = csv.writer(sys.stdout)
    writer.writerow(["agent_name", "score"])
    writer.writerows(results)


_FORMATTERS = {
    "text": output_text,
    "json": output_json,
    "csv": output_csv,
}


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run smith-game simulations.")
    debug_level = parser.add_mutually_exclusive_group(required=False)
    debug_level.add_argument("--log-level", default=logging.WARNING)
    debug_level.add_argument("-v", "--verbose", action="count", default=0)

    parser.add_argument(
        "-f",
        "--format",
        help="Output format",
        choices=tuple(_FORMATTERS.keys()),
        default="text",
    )

    builtin_agents = parser.add_mutually_exclusive_group(required=False)
    builtin_agents.add_argument("--no-builtin-agents", dest="builtin_agents", action="store_false", help="Do not load builtin agents")
    builtin_agents.add_argument("--builtin-agents", dest="builtin_agents", action="store_true", help="Load builtin agents")
    builtin_agents.set_defaults(builtin_agents=True)
    parser.add_argument("-d", "--agents-dir", help="Read agents files from the given directory", default="player_agents")

    args = parser.parse_args(args=argv)
    args.log_level -= 10 * args.verbose  # Every 10 reduces log-level by one

    return args


def main(argv=None):
    args = parse_args(argv)
    logging.basicConfig(level=args.log_level)

    agents_path = "player_agents"
    _logger.info("Loading agents from %s", agents_path)

    if args.builtin_agents:
        importlib.import_module("smithg.agents.examples")
    discover_agents(args.agents_dir)
    _logger.info("Loading done.")

    _logger.info("Running simulation...")
    agent_container = smithg.engine.simulate()

    results = [Result(cont.agent_name, cont.state.balance) for cont in agent_container]
    results.sort(key=lambda r: r.score, reverse=True)

    formatter = _FORMATTERS.get(args.format, output_text)
    formatter(results)


if __name__ == "__main__":
    main()
