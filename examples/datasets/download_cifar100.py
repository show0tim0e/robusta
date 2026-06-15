import os
from torchvision.datasets import CIFAR100
from torchvision import transforms

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "cifar100")

os.makedirs(DATA_DIR, exist_ok=True)

transform = transforms.ToTensor()

CIFAR100(DATA_DIR, train=False, download=True, transform=transform)

print(f"CIFAR-100 downloaded to {DATA_DIR}")