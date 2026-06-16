import os

import torch
from torchvision import models

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model = models.resnet18(weights="IMAGENET1K_V1")
model.fc = torch.nn.Linear(model.fc.in_features, 100)

MODEL_PATH = os.path.join(BASE_DIR, "resnet18_cifar100.pth")
torch.save(model.state_dict(), MODEL_PATH)

print(f"ResNet18 CIFAR-100 model downloaded to {MODEL_PATH}")