import torch
import torch.nn as nn
from torch.nn import Module
from torchvision import models

from ..utils import adapt_input_channels


def build_resnet18(
    num_classes: int,
    input_channels: int,
) -> Module:

    model = models.resnet18(
        weights=models.ResNet18_Weights.IMAGENET1K_V1
    )

    if input_channels != 3:

        old_weight = (
            model.conv1.weight
            .detach()
            .clone()
        )

        model.conv1 = nn.Conv2d(
            input_channels,
            64,
            kernel_size=7,
            stride=2,
            padding=3,
            bias=False,
        )

        with torch.no_grad():
            model.conv1.weight.copy_(
                adapt_input_channels(
                    old_weight,
                    input_channels,
                )
            )

    if num_classes != 1000:

        model.fc = nn.Linear(
            model.fc.in_features,
            num_classes,
        )

    return model