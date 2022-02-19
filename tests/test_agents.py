import smithg
import smithg.engine


def test_base_agent_class():
    class TestWorld(smithg.engine.engine.World):
        def process_step(self) -> None:
            pass

    registry = smithg.agents.Registry()

    world = TestWorld(
        known_items=["item"],
        balance_init=100,
        balance_increase=0,
        command_fuel_init=100,
        command_fuel_increase=25,
    )

    @registry.register_agent_class
    class TestAgent(smithg.Agent):
        def process(self, env: smithg.Environment) -> None:
            self.safe_queue_command(env, smithg.commands.Work(amount=10))

    world.add_agents_from_registry(registry)

    world.step(0)

    agent_state = world.player_agent_containers[0].state
    assert agent_state == smithg.engine.engine.AgentContainer.State(
        command_fuel=115,
        balance=200,
        items={},
    )
