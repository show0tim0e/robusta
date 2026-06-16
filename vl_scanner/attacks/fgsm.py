from typing import Any

from torch import Tensor, nn, optim, torch
from torch.nn import Module

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
        from art.attacks.evasion import FastGradientMethod
        from art.estimators.classification import PyTorchClassifier

        classifier = PyTorchClassifier(
            model=model,
            loss=nn.CrossEntropyLoss(),
            optimizer=optim.Adam(model.parameters(), lr=0.01),
            input_shape=x.shape[1:],
            nb_classes=y.shape[1] if y.ndim > 1 else int(y.max()) + 1
        )

        attack = FastGradientMethod(
            estimator=classifier,
            eps=epsilon
        )

        x_np = x.detach().cpu().numpy()

        x_adv = attack.generate(x=x_np, y=y.detach().cpu().numpy())
        return torch.from_numpy(x_adv).to(dtype=x.dtype, device=x.device)