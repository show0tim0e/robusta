from typing import Any

from torch import Tensor
from torch.nn import Module

from .base import Attack, AttackParameter


class PGD(Attack):
    @property
    def name(self) -> str:
        return "pgd"

    @property
    def description(self) -> str:
        return "Projected Gradient Descent (PGD) is an iterative adversarial attack that generates adversarial examples by repeatedly applying small perturbations to the input data in the direction of the gradient of the loss with respect to the input. The perturbations are projected back onto a specified norm ball to ensure that they remain within a certain distance from the original input. PGD is considered a stronger attack than FGSM and is often used to evaluate the robustness of machine learning models against adversarial attacks."

    @property
    def attack_parameters(self) -> list[AttackParameter]:
        return [
            AttackParameter("epsilon", float, 0.03),
            AttackParameter("alpha", float, 0.01),
            AttackParameter("num_iter", int, 40),
        ]

    def generate(
        self,
        model: Module,
        x: Tensor,
        y: Tensor,
        epsilon: float = 0.03,
        alpha: float = 0.01,
        num_iter: int = 40,
        **kwargs: Any,
    ) -> Tensor:
        return x
