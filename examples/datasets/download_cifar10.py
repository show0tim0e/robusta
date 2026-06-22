import shutil
from pathlib import Path

import torch
from torchvision import transforms
from torchvision.datasets import CIFAR10

BASE_DIR = Path(__file__).resolve().parent
TMP_DIR = BASE_DIR / "_tmp_cifar10"
PT_FILE = BASE_DIR / "cifar10.pt"


def download_cifar10() -> str:

    BASE_DIR.mkdir(parents=True, exist_ok=True)

    # temporary directory for raw data
    if TMP_DIR.exists():
        shutil.rmtree(TMP_DIR)

    transform = transforms.ToTensor()

    dataset = CIFAR10(root=str(TMP_DIR), train=False, download=True, transform=transform)

    x = torch.stack([img for img, _ in dataset])
    y = torch.tensor([label for _, label in dataset])

    torch.save({"x": x, "y": y, "name": "cifar10", "num_classes": 10}, PT_FILE)

    # clean up temporary directory
    shutil.rmtree(TMP_DIR)

    return str(PT_FILE)


if __name__ == "__main__":
    print(f"CIFAR-10 saved to {download_cifar10()}")
