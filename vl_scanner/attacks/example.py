from typing import Any

from torch import Tensor, zeros
from torch.nn import Module

from .base import Attack, AttackParameter


class ExampleAttack(Attack):
    """
    An example attack class to demonstrate how to implement the interface.
    """

    @staticmethod
    def name() -> str:
        return "Example Attack"

    @staticmethod
    def description() -> str:
        return (
            "This is a demonstration attack. It showcases how to define "
            "mandatory parameters (epsilon, alpha) and optional parameters (delta) "
            "that the UI can dynamically render."
        )

    @staticmethod
    def attack_parameters() -> list[AttackParameter]:
        return [
            AttackParameter(name="epsilon", type=float, default=0.03),
            AttackParameter(name="num_iter", type=int, default=10),
            AttackParameter(name="delta", type=float, default=None, optional=True),
        ]

    @staticmethod
    def generate(
        model: Module,
        x: Tensor,
        y: Tensor,
        epsilon: float = 0.03,
        num_iter: int = 10,
        delta: float | None = None,
        **kwargs: Any,
    ) -> Tensor:
        print(f"Running {ExampleAttack.name()} with:")
        print(f" - epsilon: {epsilon}")
        print(f" - num_iter: {num_iter}")
        print(
            f" - delta: {delta} (is {'provided' if delta is not None else 'missing'})"
        )
        return x


if __name__ == "__main__":
    # No instantiation needed for static methods
    user_input = {
        "epsilon": 0.05,
        "num_iter": 20,
    }
    ExampleAttack.generate(Module(), zeros(1), zeros(1), **user_input)
