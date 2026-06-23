from pathlib import Path
from typing import Any

import torch
from torch.nn import Module
from transformers import AutoImageProcessor, AutoModelForImageClassification


class HFImageClassifier(Module):
    """
    Adapter that makes Hugging Face image classification models
    behave like a regular PyTorch classifier returning logits.
    """

    def __init__(self, model: Module) -> None:
        super().__init__()
        self.model = model

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        outputs = self.model(pixel_values=x)
        return outputs.logits

class ModelProvider:

    @staticmethod
    def load(
        model_id: str | Path,
        *,
        device: str | None = None,
        dtype: torch.dtype | None = None,
        trust_remote_code: bool = False,
    ) -> tuple[Module, Any]:

        kwargs: dict[str, Any] = {
            "trust_remote_code": trust_remote_code,
        }

        if dtype is not None:
            kwargs["torch_dtype"] = dtype

        processor = AutoImageProcessor.from_pretrained(
            str(model_id),
            trust_remote_code=trust_remote_code,
        )

        model = AutoModelForImageClassification.from_pretrained(
            str(model_id),
            **kwargs,
        )

        if device is None:
            device = (
                "cuda"
                if torch.cuda.is_available()
                else "cpu"
            )

        model.to(device)
        model.eval()

        return (
            HFImageClassifier(model),
            processor,
        )