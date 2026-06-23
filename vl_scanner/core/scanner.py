from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

import torch
from torch import Tensor
from torch.nn import Module

from vl_scanner.attacks.base import Attack


@dataclass(slots=True, frozen=True)
class AttackConfig:
    attack: type[Attack]
    params: dict[str, Any] = field(default_factory=dict)

@dataclass(slots=True)
class AttackResult:
    attack_name: str
    attack_params: dict[str, Any]

    x_adv: Tensor
    adv_pred: Tensor
    adv_confidence: Tensor

@dataclass(slots=True)
class ScanResult:
    x: Tensor
    y: Tensor
    pred: Tensor
    confidence: Tensor
    results: list[AttackResult]

@dataclass(slots=True)
class Scanner:
    model: Module
    dataset: tuple[Tensor, Tensor]
    attacks: Sequence[AttackConfig] = field(default_factory=tuple)

    def run(self) -> ScanResult:
        x, y = self.dataset

        device = next(self.model.parameters()).device

        x = x.to(device)
        y = y.to(device)

        self.model.eval()

        # normal image classification
        with torch.no_grad():
            logits = self.model(x)

            probs = torch.softmax(logits, dim=1)
            confidence, pred = probs.max(dim=1)

        results: list[AttackResult] = []

        # run attacks
        for attack_config in self.attacks:
            x_adv = attack_config.attack.generate(
                self.model,
                x,
                y,
                **attack_config.params
            )

            with torch.no_grad():
                adv_logits = self.model(x_adv)

                adv_probs = torch.softmax(adv_logits, dim=1)
                adv_confidence, adv_pred = adv_probs.max(dim=1)

            results.append(
                AttackResult(
                    attack_name=attack_config.attack.name(),
                    attack_params=dict(attack_config.params),

                    x_adv=x_adv.detach().cpu(),
                    adv_pred=adv_pred.detach().cpu(),
                    adv_confidence=adv_confidence.detach().cpu()
                )
            )

        return ScanResult(
            x=x.detach().cpu(),
            y=y.detach().cpu(),
            pred=pred.detach().cpu(),
            confidence=confidence.detach().cpu(),
            results=results
        )