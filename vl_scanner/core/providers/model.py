from pathlib import Path

import torch
from torch.nn import Module
from transformers import AutoModelForImageClassification

from vl_scanner.core.models.checkpoint import validate_checkpoint
from vl_scanner.core.models.registry import ModelRegistry


class ModelProvider:

    @staticmethod
    def load(path: str | Path) -> Module:
        model = AutoModelForImageClassification.from_pretrained(path)

        #TODO

        # checkpoint_path = Path(path).expanduser().resolve()

        # if not checkpoint_path.exists():
        #     raise FileNotFoundError(
        #         f"Model checkpoint not found: {checkpoint_path}"
        #     )

        # checkpoint = torch.load(
        #     checkpoint_path,
        #     map_location="cpu",
        # )

        # model_checkpoint = validate_checkpoint(checkpoint)

        # model = ModelRegistry.create(
        #     model_checkpoint["architecture"],
        #     model_checkpoint["num_classes"],
        #     model_checkpoint["input_channels"],
        # )

        # model.load_state_dict(
        #     model_checkpoint["state_dict"]
        # )

        model.eval()

        return model
