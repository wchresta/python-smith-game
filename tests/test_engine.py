import collections

import smithg
import smithg.engine


def test_engine_should_create_correct_environment():
    expected_env = smithg.Environment(
        known_items=frozenset({"item"}),
        buy_offers=frozenset(),
        sell_offers=frozenset(),
        balance=100,
        command_fuel=125,
        inventory=collections.defaultdict(int),
    )

    agent_calls: list[tuple[smithg.Environment, list[smithg.events.Event]]] = []

    def test_agent(
        env: smithg.Environment, events: list[smithg.events.Event]
    ) -> list[smithg.commands.Command]:
        agent_calls.append((env, events))
        assert env == expected_env, "Received unexpected environment"
        return []

    class TestWorld(smithg.engine.engine.World):
        def process_step(self) -> None:
            pass

    world = TestWorld(
        known_items=["item"],
        balance_init=100,
        balance_increase=0,
        command_fuel_init=100,
        command_fuel_increase=25,
    )
    world.add_agent(test_agent)

    world.step(0)

    assert len(agent_calls) == 1, "World has stepped, but agent was not called"
