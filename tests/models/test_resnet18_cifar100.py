from pathlib import Path

import torch

from examples.models.download_resnet18_cifar100 import download_resnet18_cifar100
from vl_scanner.core.providers.model import ModelProvider

MODEL_PATH = Path(__file__).resolve().parents[2] / "examples" / "models" / "resnet18_cifar100.pth"


def _ensure_model_checkpoint() -> Path:
    regenerate = True
    if MODEL_PATH.exists():
        try:
            checkpoint = torch.load(MODEL_PATH, map_location="cpu")
            regenerate = not (checkpoint["format_version"] == 1 and checkpoint["framework"] == "pytorch" and checkpoint["model_type"] == "image_classification" and checkpoint["architecture"] == "resnet18" and checkpoint["num_classes"] == 100 and checkpoint["input_channels"] == 3)
        except Exception:
            regenerate = True

    if regenerate:
        generated_path = Path(download_resnet18_cifar100())
        assert generated_path == MODEL_PATH

    assert MODEL_PATH.exists()
    return MODEL_PATH


def test_resnet18_cifar100_model_download():
    model_path = _ensure_model_checkpoint()

    checkpoint = torch.load(model_path, map_location="cpu")
    assert checkpoint["format_version"] == 1
    assert checkpoint["framework"] == "pytorch"
    assert checkpoint["model_type"] == "image_classification"
    assert checkpoint["architecture"] == "resnet18"
    assert checkpoint["num_classes"] == 100
    assert checkpoint["input_channels"] == 3

    model = ModelProvider.load(model_path)
    assert not model.training

    output = model(torch.randn(2, 3, 32, 32))
    assert output.shape == (2, 100)
