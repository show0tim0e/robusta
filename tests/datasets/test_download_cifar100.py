import os

import torch

from examples.datasets.download_cifar100 import PT_FILE, download_cifar100


def test_cifar100_download():

    if os.path.exists(PT_FILE):
        os.remove(PT_FILE)

    download_cifar100()

    assert os.path.exists(PT_FILE)

    data = torch.load(PT_FILE)

    assert "x" in data
    assert "y" in data
    assert "name" in data
    assert "num_classes" in data

    assert data["x"].shape == (10000, 3, 32, 32)
    assert data["y"].shape == (10000,)
    assert data["num_classes"] == 100