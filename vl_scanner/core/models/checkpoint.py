from typing import Any, TypedDict, cast

from torch import Tensor


class ModelCheckpoint(TypedDict):

    format_version: int
    framework: str
    model_type: str
    architecture: str
    num_classes: int
    input_channels: int
    state_dict: dict[str, Tensor]



def validate_checkpoint(
    checkpoint: dict[str, Any],
) -> ModelCheckpoint:

    required_keys = {
        "format_version",
        "framework",
        "model_type",
        "architecture",
        "num_classes",
        "input_channels",
        "state_dict",
    }

    missing_keys = required_keys.difference(
        checkpoint
    )

    if missing_keys:
        raise ValueError(
            f"Missing checkpoint fields: {missing_keys}"
        )


    if checkpoint["format_version"] != 1:
        raise ValueError(
            "Unsupported checkpoint version"
        )


    if checkpoint["framework"].lower() != "pytorch":
        raise ValueError(
            "Unsupported framework"
        )


    if checkpoint["model_type"].lower() != "image_classification":
        raise ValueError(
            "Unsupported model type"
        )


    if not isinstance(
        checkpoint["state_dict"],
        dict,
    ):
        raise TypeError(
            "state_dict must be a dictionary"
        )


    return cast(
        ModelCheckpoint,
        checkpoint,
    )