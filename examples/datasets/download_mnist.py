import os
import shutil

import torch
from torchvision import transforms
from torchvision.datasets import MNIST

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TMP_DIR = os.path.join(BASE_DIR, "_tmp_mnist")
PT_FILE = os.path.join(BASE_DIR, "mnist.pt")


def download_mnist():

    os.makedirs(BASE_DIR, exist_ok=True)

    # temporary directory for raw data
    if os.path.exists(TMP_DIR):
        shutil.rmtree(TMP_DIR)

    transform = transforms.ToTensor()

    dataset = MNIST(
        root=TMP_DIR,
        train=False,
        download=True,
        transform=transform
    )

    x = torch.stack([img for img, _ in dataset])
    y = torch.tensor([label for _, label in dataset])

    torch.save(
        {
            "x": x,
            "y": y,
            "name": "mnist",
            "num_classes": 10
        },
        PT_FILE
    )

    # clean up temporary directory
    shutil.rmtree(TMP_DIR)

    return PT_FILE


if __name__ == "__main__":
    print(f"MNIST saved to {download_mnist()}")