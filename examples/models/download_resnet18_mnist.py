from pathlib import Path

import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset
from torchvision import models

from tests.datasets.test_mnist import _ensure_dataset_artifact
from vl_scanner.core.providers.dataset import DatasetProvider

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "resnet18_mnist.pth"
FORMAT_VERSION = 1
FRAMEWORK = "pytorch"
MODEL_TYPE = "image_classification"
ARCHITECTURE = "resnet18"
NUM_CLASSES = 10
INPUT_CHANNELS = 1


def download_resnet18_mnist() -> str:

    x, y = DatasetProvider.load(_ensure_dataset_artifact())

    dataset = TensorDataset(x, y)

    loader = DataLoader(
        dataset,
        batch_size=64,
        shuffle=True,
    )


    model = models.resnet18(
        weights=models.ResNet18_Weights.IMAGENET1K_V1
    )


    model.conv1 = nn.Conv2d(
        INPUT_CHANNELS,
        64,
        kernel_size=7,
        stride=2,
        padding=3,
        bias=False,
    )


    model.fc = nn.Linear(
        model.fc.in_features,
        NUM_CLASSES,
    )


    device = torch.device(
        "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )

    model.to(device)


    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=1e-3,
    )

    criterion = nn.CrossEntropyLoss()


    model.train()


    epochs = 3

    for _ in range(epochs):

        for images, labels in loader:

            images = images.to(device)
            labels = labels.to(device)


            optimizer.zero_grad()

            output = model(images)

            loss = criterion(
                output,
                labels,
            )

            loss.backward()

            optimizer.step()


    model.eval()


    torch.save(
        {
            "format_version": FORMAT_VERSION,
            "framework": FRAMEWORK,
            "model_type": MODEL_TYPE,
            "architecture": ARCHITECTURE,
            "num_classes": NUM_CLASSES,
            "input_channels": INPUT_CHANNELS,
            "dataset": "mnist",
            "state_dict": model.state_dict(),
        },
        MODEL_PATH,
    )


    return str(MODEL_PATH)


if __name__ == "__main__":
    print(
        f"ResNet18 MNIST model created at {download_resnet18_mnist()}"
    )