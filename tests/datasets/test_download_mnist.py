import os

import torch

from examples.datasets.download_mnist import PT_FILE, download_mnist


def test_mnist_download():

    if os.path.exists(PT_FILE):
        os.remove(PT_FILE)

    download_mnist()

    assert os.path.exists(PT_FILE)

    data = torch.load(PT_FILE)

    assert "x" in data
    assert "y" in data
    assert "name" in data
    assert "num_classes" in data

    assert data["x"].shape == (10000, 1, 28, 28)
    assert data["y"].shape == (10000,)
    assert data["num_classes"] == 10