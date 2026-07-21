from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from torch import Tensor
    from torch.nn import Module

from .base import Attack, AttackParameter


class FGSM(Attack):
    @staticmethod
    def name() -> str:
        return "FGSM"

    @staticmethod
    def description() -> str:
        return ("Fast Gradient Sign Method (FGSM) is a simple and efficient adversarial attack that generates "
                "adversarial examples by adding a perturbation to the input in the direction of the gradient of "
                "the loss with respect to the input. The perturbation is scaled by a factor 'epsilon', which "
                "controls the strength of the attack. FGSM is computationally efficient and is commonly used to quickly "
                "evaluate the robustness of machine learning models against adversarial attacks.")

    @staticmethod
    def attack_parameters() -> list[AttackParameter]:
        return [
            AttackParameter("epsilon", float, 0.03, description="Maximum allowed perturbation of the original input."),
        ]

    @staticmethod
    def generate(
        model: Module,
        x: Tensor,
        y: Tensor,
        epsilon: float = 0.03,
        **kwargs: Any
    ) -> Tensor:
        import torch
        from art.attacks.evasion import FastGradientMethod
        from art.estimators.classification import PyTorchClassifier
        from torch import nn

        # finds out on what device the model is running (GPU or CPU)
        device = next(model.parameters()).device

        # gets the number of classes
        with torch.no_grad():
            n_classes = model(x[:1].to(device)).shape[-1]

        # ART doesn't work with PyTorch-models, so we must wrap it into a classifier
        classifier = PyTorchClassifier(
            model=model,
            loss=nn.CrossEntropyLoss(),
            input_shape=x.shape[1:],
            nb_classes=n_classes,
            clip_values=(0.0, 1.0),
            device_type="gpu" if device.type == "cuda" else "cpu"
        )

        # ART only works with numpy arrays
        x_np = x.detach().cpu().numpy()
        y_np = y.detach().cpu().numpy()

        # the actual attack
        attack = FastGradientMethod(
            estimator=classifier,
            eps=epsilon
        )

        x_adv = attack.generate(
            x=x_np,
            y=y_np
        )
        return torch.from_numpy(x_adv).to(dtype=x.dtype, device=x.device)
