from typing import Any

from torch import Tensor, zeros
from torch.nn import Module

from .base import Attack, AttackParameter


class ExampleAttack(Attack):
    """
    An example attack class to demonstrate how to implement the interface.
    """

    @property
    def name(self) -> str:
        return "Example Attack"

    @property
    def description(self) -> str:
        return (
            "This is a demonstration attack. It showcases how to define "
            "mandatory parameters (epsilon, alpha) and optional parameters (delta) "
            "that the UI can dynamically render."
        )

    @property
    def attack_parameters(self) -> list[AttackParameter]:
        return [
            AttackParameter(name="epsilon", type=float, default=0.03),
            AttackParameter(name="num_iter", type=int, default=10),
            AttackParameter(name="delta", type=float, default=None, optional=True),
        ]

    def generate(
        self,
        model: Module,
        x: Tensor,
        y: Tensor,
        epsilon: float = 0.03,
        num_iter: int = 10,
        delta: float | None = None,
        **kwargs: Any,
    ) -> Tensor:
        print(f"Running {self.name} with:")
        print(f" - epsilon: {epsilon}")
        print(f" - num_iter: {num_iter}")
        print(
            f" - delta: {delta} (is {'provided' if delta is not None else 'missing'})"
        )
        return x


if __name__ == "__main__":
    attack = ExampleAttack()
    user_input = {
        "epsilon": 0.05,
        "num_iter": 20,
    }
    attack.generate(Module(), zeros(1), zeros(1), **user_input)
