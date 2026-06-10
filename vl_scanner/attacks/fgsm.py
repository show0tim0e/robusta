from typing import Any

from torch import tensor, nn, optim
from torch.nn import Module

from .base import Attack, AttackParameter

from art.estimators.classification import PyTorchClassifier
from art.attacks.evasion import FastGradientMethod

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
            x: tensor,
            y: tensor,
            epsilon: float = 0.03,
            nb_classes: int = 10, # Anzahl an Ausgabeklassen für das Modell
            **kwargs: Any
    ) -> tensor:
        classifier = PyTorchClassifier(
            model=model,
            loss=nn.CrossEntropyLoss(),
            optimizer=optim.Adam(model.parameters(), lr=0.01),
            input_shape=x.shape[1:],
            nb_classes=nb_classes
        )

        attack = FastGradientMethod(
            estimator=classifier,
            eps=epsilon
        )

        x_np = x.detach().cpu().numpy()

        x_adv = attack.generate(x=x_np)
        return tensor(x_adv, dtype=x.dtype, device=x.device)