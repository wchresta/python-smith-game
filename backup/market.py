
# Simulate a run with the given number of steps
def simulate(steps=1000) -> None:
    for s in range(steps):
        step(s)


def step(s: int) -> None:
    print(f"Step {s}")

