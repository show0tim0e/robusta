from pathlib import Path

import torch

from examples.models.download_resnet18_mnist import download_resnet18_mnist
from tests.datasets.test_mnist import _ensure_dataset_artifact
from vl_scanner.core.providers.dataset import DatasetProvider
from vl_scanner.core.providers.model import ModelProvider

MODEL_PATH = Path(__file__).resolve().parents[2] / "examples" / "models" / "resnet18_mnist.pth"


def _ensure_model_checkpoint() -> Path:
    regenerate = True
    if MODEL_PATH.exists():
        try:
            checkpoint = torch.load(MODEL_PATH, map_location="cpu")
            regenerate = not (checkpoint["format_version"] == 1 and checkpoint["framework"] == "pytorch" and checkpoint["model_type"] == "image_classification" and checkpoint["architecture"] == "resnet18" and checkpoint["num_classes"] == 10 and checkpoint["input_channels"] == 1)
        except Exception:
            regenerate = True

    if regenerate:
        generated_path = Path(download_resnet18_mnist())
        assert generated_path == MODEL_PATH

    assert MODEL_PATH.exists()
    return MODEL_PATH


def test_resnet18_mnist_model_download():
    model_path = _ensure_model_checkpoint()

    checkpoint = torch.load(model_path, map_location="cpu")
    assert checkpoint["format_version"] == 1
    assert checkpoint["framework"] == "pytorch"
    assert checkpoint["model_type"] == "image_classification"
    assert checkpoint["architecture"] == "resnet18"
    assert checkpoint["num_classes"] == 10
    assert checkpoint["input_channels"] == 1

    model = ModelProvider.load(model_path)
    assert not model.training

    output = model(torch.randn(2, 1, 28, 28))
    assert output.shape == (2, 10)

    # check model classification with examples from dataset

    x, y = DatasetProvider.load(_ensure_dataset_artifact())

    model.eval()

    with torch.no_grad():

        print("Different predictions: (having some differences is expected, but we want to check if there are any major issues)")

        for i in range(100):

            image = x[i].unsqueeze(0)
            label = y[i]

            output = model(image)

            probabilities = torch.softmax(
                output,
                dim=1,
            )

            confidence, prediction = torch.max(
                probabilities,
                dim=1,
            )

            if label != prediction.item():
                print(f"Image {i}: True Label = {label}, Predicted Label = {prediction.item()}, Confidence = {confidence.item():.4f}")