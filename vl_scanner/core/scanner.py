import random
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

import torch
from torch import Tensor
from torch.nn import Module

from vl_scanner.attacks.base import Attack
from vl_scanner.core.providers.dataset import DatasetProvider
from vl_scanner.core.providers.model import ModelProvider


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
    model: Module | None = None
    processor: Any | None = None
    dataset: tuple[Tensor, Tensor] | None = None
    attacks: Sequence[AttackConfig] = field(default_factory=tuple)

    def set_model(
        self,
        model_id: str,
        *,
        device: str | None = None,
        dtype: torch.dtype | None = None,
        trust_remote_code: bool = False
    ) -> bool:
        try:
            model, processor = ModelProvider.load(
                model_id=model_id,
                device=device,
                dtype=dtype,
                trust_remote_code=trust_remote_code
            )
        
        except Exception:
            return False
        
        self.model = model
        self.processor = processor

        return True
    
    def set_dataset(
        self,
        dataset_id: str,
        *,
        split: str = "test",
        size: int | None = None
    ) -> bool:
        try:
            dataset = DatasetProvider.load(
                dataset_id=dataset_id,
                split=split
            )

            if size is not None:
                random_indices = random.sample(
                    range(len(dataset)),
                    size
                )

                dataset = dataset.select(random_indices)

            images = DatasetProvider.get_images(dataset)
            labels = DatasetProvider.get_labels(dataset)

            if len(images) != len(labels):
                return False
            
            if self.processor is None:
                return False
            
            encoded = self.processor(
                images=list(images),
                return_tensors="pt",
                do_normalize=True
            )

            x = encoded["pixel_values"]
            y = torch.tensor(list(labels))
        
        except Exception:
            return False

        self.dataset = (x, y)

        return True
    
    def set_attacks(
        self,
        attacks: Sequence[AttackConfig]
    ) -> None:
        self.attacks = tuple(attacks)

    def ready(self) -> bool:
        return (
            self.model is not None and
            self.processor is not None and
            self.dataset is not None and
            len(self.attacks) > 0
        )

    def run(self) -> ScanResult:
        if not self.ready():
            raise RuntimeError("Scanner is not ready. Please set model, dataset, and attacks first.")

        assert self.dataset is not None
        x, y = self.dataset

        assert self.model is not None
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