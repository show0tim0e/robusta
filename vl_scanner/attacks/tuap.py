from typing import Any

import numpy as np
from art.attacks.evasion import TargetedUniversalPerturbation
from art.estimators.classification import PyTorchClassifier
from torch import Tensor, nn, torch
from torch.nn import Module

from .base import Attack, AttackParameter


class TUAP(Attack):
    @staticmethod
    def name() -> str:
        return "tuap"

    @staticmethod
    def description() -> str:
        return "Targeted Universal Adversarial Perturbation (TUAP) berechnet eine einzige, eingabe-unabhängige Perturbation, die, addiert auf (fast) beliebige Eingaben, das Modell dazu bringt, eine bestimmte Zielklasse vorherzusagen. Die Perturbation wird iterativ aus einem Batch repräsentativer Eingaben gelernt: für jedes noch nicht erfolgreich umgelenkte Sample wird ein innerer, gezielter Angriff (Standard: FGSM) genutzt, um die gemeinsame Perturbation in Richtung der Zielklasse zu verschieben. Anschließend wird sie auf eine Lp-Kugel mit Radius 'eps' projiziert. Im Gegensatz zu PGD ist das Ergebnis 'universal': dieselbe Perturbation funktioniert über viele verschiedene Eingaben hinweg und kann auch auf neue, ungesehene Samples übertragen werden. Unterstützte innere Angriffe sind 'fgsm' und 'simba'."

    @staticmethod
    def attack_parameters() -> list[AttackParameter]:
        return [
            AttackParameter("target_class", int, 0),
            AttackParameter("eps", float, 0.1),
            AttackParameter("delta", float, 0.2),
            AttackParameter("max_iter", int, 20),
            AttackParameter("attacker_eps", float, 0.03)
        ]

    @staticmethod
    def generate(
        model: Module,
        x: Tensor,
        y: Tensor,
        target_class: int = 0,
        eps: float = 0.1,
        delta: float = 0.2,
        max_iter: int = 20,
        attacker_eps: float = 0.03,
        **kwargs: Any,
    ) -> Tensor:

        device = next(model.parameters()).device

        with torch.no_grad():
            n_classes = model(x[:1].to(device)).shape[-1]
        
        classifier = PyTorchClassifier(
            model=model,
            loss=nn.CrossEntropyLoss(),
            input_shape=x.shape[1:],
            nb_classes=n_classes
        )

        x_np = x.detach().cpu().numpy()

        y_target = np.zeros((x_np.shape[0], classifier.nb_classes), dtype=np.float32)
        y_target[:, target_class] = 1.0

        attack = TargetedUniversalPerturbation(
            classifier=classifier,
            attacker="fgsm",
            attacker_params={"eps": attacker_eps, "targeted": True},
            delta=delta,
            max_iter=max_iter,
            eps=eps,
            norm="inf"
        )

        x_adv = attack.generate(x=x_np, y=y_target)
        return torch.from_numpy(x_adv).to(dtype=x.dtype, device=x.device)