from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from torch import Tensor
    from torch.nn import Module

from .base import Attack, AttackParameter


class TUAP(Attack):
    @staticmethod
    def name() -> str:
        return "tuap"

    @staticmethod
    def description() -> str:
        return "Targeted Universal Adversarial Perturbation (TUAP) computes a single, input-independent perturbation that, when added to (almost) any input, causes the model to predict a specific target class. The perturbation is learned iteratively from a batch of representative inputs: for each sample that has not yet been successfully redirected, an internal, targeted attack (FGSM) is used to shift the joint perturbation toward the target class. It is then projected onto an Lp sphere with radius ‘eps’. Unlike PGD, the result is ‘universal’: the same perturbation works across many different inputs and can also transfer to new, unseen samples."

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

        import numpy as np
        import torch
        from art.attacks.evasion import TargetedUniversalPerturbation
        from art.estimators.classification import PyTorchClassifier
        from torch import nn

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
