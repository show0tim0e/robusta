from dataclasses import dataclass
from typing import Any

from torch import Tensor
from torch.nn import Module

from .base import Attack


@dataclass(slots=True)
class PGD(Attack):
    def name(self) -> str:
        return "pgd"
    
    def description(self) -> str:
        return "Projected Gradient Descent (PGD) is an iterative adversarial attack that generates adversarial examples by repeatedly applying small perturbations to the input data in the direction of the gradient of the loss with respect to the input. The perturbations are projected back onto a specified norm ball to ensure that they remain within a certain distance from the original input. PGD is considered a stronger attack than FGSM and is often used to evaluate the robustness of machine learning models against adversarial attacks."
    
    def get_params(self) -> dict[str,Any]:
        pass

    def generate(self, model: Module, x: Tensor, y: Tensor, params: dict[str,Any]) -> Tensor:
        pass