from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from torch import Tensor
    from torch.nn import Module

from .base import Attack, AttackParameter


class TUAP(Attack):
    @staticmethod
    def name() -> str:
        return "TUAP"

    @staticmethod
    def description() -> str:
        return (
            "Targeted Universal Adversarial Perturbation (TUAP) computes a single, input-independent perturbation that, "
            "when added to (almost) any input, causes the model to predict a specific target class. The perturbation is "
            "learned iteratively from a batch of representative inputs. For each sample that has not yet been successfully "
            "redirected, an internal targeted attack (FGSM) is used to update the shared perturbation toward the target class. "
            "The resulting perturbation is then projected onto an Lp sphere with radius 'epsilon'. Unlike PGD, the resulting "
            "perturbation is universal: the same perturbation works across many different inputs and can also transfer to "
            "previously unseen samples."
        )

    @staticmethod
    def attack_parameters() -> list[AttackParameter]:
        return [
            AttackParameter("target_class", int, 0, description="Target class that the model should predict for the perturbed input."),
            AttackParameter("eps", float, 0.1, description="Maximum allowed perturbation of the original input."),
            AttackParameter("delta", float, 0.2, description="Target success rate (1 - delta). The attack stops once this success rate is reached."),
            AttackParameter("max_iter", int, 20, description="Maximum number of iterations over the dataset when generating a universal perturbation."),
            AttackParameter("attacker_eps", float, 0.03, description="Maximum perturbation used by the internal attack (FGSM)."),
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
