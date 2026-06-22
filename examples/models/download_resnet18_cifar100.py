#TODO
from pathlib import Path

import torch
from torchvision import models

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "resnet18_cifar100.pth"
FORMAT_VERSION = 1
FRAMEWORK = "pytorch"
MODEL_TYPE = "image_classification"
ARCHITECTURE = "resnet18"
NUM_CLASSES = 100
INPUT_CHANNELS = 3


def download_resnet18_cifar100() -> str:
    model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
    model.fc = torch.nn.Linear(model.fc.in_features, NUM_CLASSES)

    torch.save(
        {
            "format_version": FORMAT_VERSION,
            "framework": FRAMEWORK,
            "model_type": MODEL_TYPE,
            "architecture": ARCHITECTURE,
            "num_classes": NUM_CLASSES,
            "input_channels": INPUT_CHANNELS,
            "state_dict": model.state_dict(),
        },
        MODEL_PATH,
    )

    return str(MODEL_PATH)


if __name__ == "__main__":
    print(f"ResNet18 CIFAR-100 model downloaded to {download_resnet18_cifar100()}")
