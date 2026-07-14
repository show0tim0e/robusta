from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import torch
    from torch.nn import Module

    HFImageClassifier = Module


def _build_hf_image_classifier() -> type[Module]:
    """Build the HFImageClassifier nn.Module subclass on first use.

    Defers the torch import until the user actually loads a model.
    """
    from torch.nn import Module

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

        @property
        def config(self):
            return self.model.config

    return HFImageClassifier


class ModelProvider:

    @staticmethod
    def load(
        model_id: str,
        *,
        device: str | None = None,
        dtype: torch.dtype | None = None,
        trust_remote_code: bool = False,
    ) -> tuple[Module, Any]:

        import torch
        from transformers import AutoImageProcessor, AutoModelForImageClassification

        HFImageClassifier = _build_hf_image_classifier()

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
