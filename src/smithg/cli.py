import smithg.engine
import smithg.agents.agents

import logging


def main():
    logging.basicConfig(level=logging.DEBUG)
    logging.info("Running market...")

    agents = [smithg.agents.agents.RandomAgent() for _ in range(30)]

    agent_container = smithg.engine.simulate(player_agents=agents)

    logging.info("Simulation finished. Here are the results")
    for cont in agent_container:
        logging.info("Agent %s, balance: %i", id(cont), cont.state.balance)


if __name__ == "__main__":
    main()
