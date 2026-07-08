from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from torch import Tensor
    from torch.nn import Module

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
            AttackParameter("num_iter", int, 40)
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
        import numpy as np
        import torch
        from art.attacks.evasion import ProjectedGradientDescent
        from art.estimators.classification import PyTorchClassifier
        from torch import nn

        device = next(model.parameters()).device

        with torch.no_grad():
            n_classes = model(x[:1].to(device)).shape[-1]

        classifier = PyTorchClassifier(
            model=model,
            loss=nn.CrossEntropyLoss(),
            input_shape=x.shape[1:],
            nb_classes=n_classes,
            clip_values=(0.0, 1.0),
            device_type="gpu" if device.type == "cuda" else "cpu"
        )

        x_np = x.detach().cpu().numpy()
        y_np = y.detach().cpu().numpy()

        attack = ProjectedGradientDescent(
            estimator=classifier,
            eps=epsilon,
            eps_step=alpha,
            max_iter=num_iter,
            targeted=False,
            norm="inf"
        )

        if y_np.ndim == 1:
            y_onehot = np.eye(n_classes)[y_np]
        else:
            y_onehot = y_np

        x_adv_np = attack.generate(
            x=x_np,
            y=y_onehot
        )

        return torch.from_numpy(x_adv_np).to(device=device, dtype=x.dtype)
