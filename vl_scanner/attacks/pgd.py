from typing import Any

import torch
from torch import Tensor
from torch.nn import Module
from torch.nn import functional as F

from .base import Attack, AttackParameter


class PGD(Attack):
    @staticmethod
    def name() -> str:
        return "pgd"

    @staticmethod
    def description() -> str:
        return "Projected Gradient Descent (PGD) is an iterative adversarial attack that generates adversarial examples by repeatedly applying small perturbations to the input data in the direction of the gradient of the loss with respect to the input. The perturbations are projected back onto a specified norm ball to ensure that they remain within a certain distance from the original input. PGD is considered a stronger attack than FGSM and is often used to evaluate the robustness of machine learning models against adversarial attacks."

    @staticmethod
    def attack_parameters() -> list[AttackParameter]:
        return [
            AttackParameter("epsilon", float, 0.03),
            AttackParameter("alpha", float, 0.01),
            AttackParameter("num_iter", int, 40),
        ]

    @staticmethod
    def generate(
        model: Module,
        x: Tensor,
        y: Tensor,
        epsilon: float = 0.03,
        alpha: float = 0.01,
        num_iter: int = 40,
        **kwargs: Any,
    ) -> Tensor:
        x_adv = x.clone().detach()

        for i in range (num_iter):
            x_adv.requires_grad = True

            logits = model(x_adv)
            loss = F.cross_entropy(logits, y)

            model.zero_grad()
            loss.backward()

            with torch.no_grad():
                x_adv = x_adv + alpha * x_adv.grad.sign()

                delta = torch.clamp(x_adv - x, min=-epsilon, max=epsilon)
                x_adv = torch.clamp(x + delta, min=0.0, max=1.0).detach()

        return x_adv


