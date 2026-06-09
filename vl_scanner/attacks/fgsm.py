from typing import Any

from torch import Tensor
from torch.nn import Module

from .base import Attack, AttackParameter


class FGSM(Attack):
    @property
    def name(self) -> str:
        return "fgsm"

    @property
    def description(self) -> str:
        return "Fast Gradient Sign Method (FGSM) is a simple and efficient adversarial attack that generates adversarial examples by adding perturbations to the input data in the direction of the gradient of the loss with respect to the input. The perturbation is scaled by a factor called epsilon, which controls the strength of the attack. FGSM is designed to be computationally efficient and can be used to quickly evaluate the robustness of machine learning models against adversarial attacks."

    @property
    def attack_parameters(self) -> list[AttackParameter]:
        return [AttackParameter("epsilon", float, 0.03)]

    def generate(
        self, model: Module, x: Tensor, y: Tensor, epsilon: float = 0.03, **kwargs: Any
    ) -> Tensor:
        return x
