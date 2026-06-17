from typing import Any

import torch
from torch import Tensor
from torch.nn import Module
from torch.nn import functional as F

from .base import Attack, AttackParameter


class FGSM(Attack):
    @staticmethod
    def name() -> str:
        return "fgsm"

    @staticmethod
    def description() -> str:
        return "Fast Gradient Sign Method (FGSM) is a simple and efficient adversarial attack that generates adversarial examples by adding perturbations to the input data in the direction of the gradient of the loss with respect to the input. The perturbation is scaled by a factor called epsilon, which controls the strength of the attack. FGSM is designed to be computationally efficient and can be used to quickly evaluate the robustness of machine learning models against adversarial attacks."

    @staticmethod
    def attack_parameters() -> list[AttackParameter]:
        return [AttackParameter("epsilon", float, 0.03)]

    @staticmethod
    def generate(
        model: Module,
            x: Tensor,
            y: Tensor,
            epsilon: float = 0.03,
            **kwargs: Any
    ) -> Tensor:
        y = y.long()
        x_adv = x.clone().detach().requires_grad_(True)

        logits = model(x_adv)
        loss = F.cross_entropy(logits, y)

        model.zero_grad()
        loss.backward()

        with torch.no_grad():
            x_adv = x + epsilon * x_adv.grad.sign()
            x_adv = torch.clamp(x_adv, min=0.0, max=1.0)

        return x_adv