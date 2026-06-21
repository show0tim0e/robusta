import os
import shutil

import torch
from torchvision import transforms
from torchvision.datasets import CIFAR100

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TMP_DIR = os.path.join(BASE_DIR, "_tmp_cifar100")
PT_FILE = os.path.join(BASE_DIR, "cifar100.pt")


def download_cifar100():

    os.makedirs(BASE_DIR, exist_ok=True)

    # temporary directory for raw data
    if os.path.exists(TMP_DIR):
        shutil.rmtree(TMP_DIR)

    transform = transforms.ToTensor()

    dataset = CIFAR100(
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
            "name": "cifar100",
            "num_classes": 100
        },
        PT_FILE
    )

    # clean up temporary directory
    shutil.rmtree(TMP_DIR)

    return PT_FILE


if __name__ == "__main__":
    print(f"CIFAR-100 saved to {download_cifar100()}")