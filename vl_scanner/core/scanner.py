from __future__ import annotations

import random
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
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
    attack_time_seconds: float

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
    token: str | None = None
    model: Module | None = None
    processor: Any | None = None
    dataset: tuple[Tensor, Tensor] | None = None
    attacks: Sequence[AttackConfig] = field(default_factory=tuple)

    def set_token(self, token: str) -> bool:
        import huggingface_hub
        try:
            huggingface_hub.login(
                token=token,
            )
            self.token = token

            return True

        except Exception:
            return False

    def set_model(self, model_id: str, *, device: str | None = None, dtype: torch.dtype | None = None, trust_remote_code: bool = False) -> bool:
        if not self.logged_in():
            return False

        from vl_scanner.core.providers.model import ModelProvider

        try:
            model, processor = ModelProvider.load(model_id=model_id, device=device, dtype=dtype, trust_remote_code=trust_remote_code)

        except Exception:
            return False

        self.model = model
        self.processor = processor

        return True

    def set_dataset(self, dataset_id: str, *, split: str = "test", size: int | None = None) -> bool:
        if not self.logged_in():
            return False

        import torch

        from vl_scanner.core.providers.dataset import DatasetProvider

        try:
            dataset = DatasetProvider.load(dataset_id=dataset_id, split=split)

            if size is not None:
                random_indices = random.sample(range(len(dataset)), size)

                dataset = dataset.select(random_indices)

            images = DatasetProvider.get_images(dataset)
            labels = DatasetProvider.get_labels(dataset)

            if len(images) != len(labels):
                return False

            if self.processor is None:
                return False

            encoded = self.processor(images=list(images), return_tensors="pt", do_normalize=True)

            x = encoded["pixel_values"]
            y = torch.tensor(list(labels))

        except Exception:
            return False

        self.dataset = (x, y)

        return True

    def set_attacks(self, attacks: Sequence[AttackConfig]) -> None:
        self.attacks = tuple(attacks)

    def logged_in(self) -> bool:
        import huggingface_hub
        try:
            huggingface_hub.whoami()
            return True
        except Exception:
            return False

    def ready(self) -> bool:
        return self.logged_in() and self.model is not None and self.processor is not None and self.dataset is not None and len(self.attacks) > 0

    def run(self, progress_callback=None, batch_size: int = 16) -> ScanResult:
        import torch

        if not self.ready():
            raise RuntimeError("Scanner is not ready. Please set token, model, dataset, and attacks first.")

        assert self.dataset is not None
        x, y = self.dataset

        assert self.model is not None
        device = next(self.model.parameters()).device

        self.model.eval()

        num_samples = len(x)

        def update_progress(percent: float, message: str) -> None:
            percent = max(0.0, min(1.0, percent))  # Clamp percent to [0.0, 1.0]

            if progress_callback is not None:
                progress_callback(percent, message)

        pred = torch.empty(num_samples, dtype=torch.long)
        confidence = torch.empty(num_samples, dtype=torch.float)

        update_progress(0, "Normal Classification")

        with torch.no_grad():
            for start in range(0, num_samples, batch_size):
                end = min(start + batch_size, num_samples)
                x_batch = x[start:end].to(device)

                logits = self.model(x_batch)
                probs = torch.softmax(logits, dim=1)
                batch_confidence, batch_pred = probs.max(dim=1)

                pred[start:end] = batch_pred.cpu()
                confidence[start:end] = batch_confidence.cpu()

                update_progress((start + batch_size) / num_samples, "Running Normal Classification")

                del x_batch, logits, probs, batch_confidence, batch_pred

        results: list[AttackResult] = []

        for attack_config in self.attacks:
            update_progress(0, f"Running Attack: {attack_config.attack.name()}")

            x_adv = torch.empty_like(x)
            adv_pred = torch.empty_like(pred)
            adv_confidence = torch.empty_like(confidence)

            start_time = datetime.now()

            for start in range(0, num_samples, batch_size):
                end = min(start + batch_size, num_samples)

                x_batch = x[start:end].to(device)
                y_batch = y[start:end].to(device)

                x_adv_batch = attack_config.attack.generate(self.model, x_batch, y_batch, **attack_config.params)

                with torch.no_grad():
                    adv_logits = self.model(x_adv_batch)
                    adv_probs = torch.softmax(adv_logits, dim=1)
                    batch_adv_confidence, batch_adv_pred = adv_probs.max(dim=1)

                x_adv[start:end] = x_adv_batch.detach().cpu()
                adv_pred[start:end] = batch_adv_pred.detach().cpu()
                adv_confidence[start:end] = batch_adv_confidence.detach().cpu()

                update_progress((start + batch_size) / num_samples, f"Running Attack: {attack_config.attack.name()}")

                del x_batch, y_batch, x_adv_batch, adv_logits, adv_probs, batch_adv_confidence, batch_adv_pred

            results.append(
                AttackResult(
                    attack_name=attack_config.attack.name(),
                    attack_params=dict(attack_config.params),
                    attack_time_seconds=(datetime.now() - start_time).total_seconds(),
                    x_adv=x_adv,
                    adv_pred=adv_pred,
                    adv_confidence=adv_confidence
                )
            )

        return ScanResult(
            x=x,
            y=y,
            pred=pred,
            confidence=confidence,
            results=results
        )


    # deprecated: run_no_batching is kept for backward compatibility, but it is recommended to use run() instead.
    # progress_callback won't work here, as it is not implemented correctly in this method
    def run_no_batching(self, progress_callback=None) -> ScanResult:
        import torch

        if not self.ready():
            raise RuntimeError("Scanner is not ready. Please set token, model, dataset, and attacks first.")

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
        total = len(self.attacks)

        # run attacks
        for i, attack_config in enumerate(self.attacks):
            # Update ProgressBar
            if progress_callback is not None:
                progress_callback(i + 1, total, attack_config.attack.name())

            time = datetime.now()

            x_adv = attack_config.attack.generate(self.model, x, y, **attack_config.params)

            with torch.no_grad():
                adv_logits = self.model(x_adv)

                adv_probs = torch.softmax(adv_logits, dim=1)
                adv_confidence, adv_pred = adv_probs.max(dim=1)

            attack_time_seconds = (datetime.now() - time).total_seconds()

            results.append(AttackResult(attack_name=attack_config.attack.name(), attack_params=dict(attack_config.params), attack_time_seconds=attack_time_seconds, x_adv=x_adv.detach().cpu(), adv_pred=adv_pred.detach().cpu(), adv_confidence=adv_confidence.detach().cpu()))

        return ScanResult(x=x.detach().cpu(), y=y.detach().cpu(), pred=pred.detach().cpu(), confidence=confidence.detach().cpu(), results=results)
