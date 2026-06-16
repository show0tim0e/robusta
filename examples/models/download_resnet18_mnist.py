import os

import torch
from torchvision import models

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model = models.resnet18(weights="IMAGENET1K_V1")

model.conv1 = torch.nn.Conv2d(
    1, 64, kernel_size=7, stride=2, padding=3, bias=False
)

model.fc = torch.nn.Linear(model.fc.in_features, 10)

MODEL_PATH = os.path.join(BASE_DIR, "resnet18_mnist.pth")
torch.save(model.state_dict(), MODEL_PATH)

print(f"ResNet18 MNIST model downloaded to {MODEL_PATH}")