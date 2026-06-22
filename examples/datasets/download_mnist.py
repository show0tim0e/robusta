import shutil
from pathlib import Path

import torch
from torchvision import transforms
from torchvision.datasets import MNIST

BASE_DIR = Path(__file__).resolve().parent
TMP_DIR = BASE_DIR / "_tmp_mnist"
PT_FILE = BASE_DIR / "mnist.pt"


def download_mnist() -> str:

    BASE_DIR.mkdir(parents=True, exist_ok=True)

    # temporary directory for raw data
    if TMP_DIR.exists():
        shutil.rmtree(TMP_DIR)

    transform = transforms.ToTensor()

    dataset = MNIST(root=str(TMP_DIR), train=False, download=True, transform=transform)

    x = torch.stack([img for img, _ in dataset])
    y = torch.tensor([label for _, label in dataset])

    torch.save({"x": x, "y": y, "name": "mnist", "num_classes": 10}, PT_FILE)

    # clean up temporary directory
    shutil.rmtree(TMP_DIR)

    return str(PT_FILE)


if __name__ == "__main__":
    print(f"MNIST saved to {download_mnist()}")
