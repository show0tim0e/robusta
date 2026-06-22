from .builders import build_resnet18
from .registry import ModelRegistry

ModelRegistry.register(
    "resnet18",
    build_resnet18,
)