import os

from torchvision import transforms
from torchvision.datasets import MNIST

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "mnist")

os.makedirs(DATA_DIR, exist_ok=True)

transform = transforms.ToTensor()

MNIST(root=DATA_DIR, train=False, download=True, transform=transform)

print(f"MNIST downloaded to {DATA_DIR}")