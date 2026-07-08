from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from datasets import ClassLabel, Dataset, Image


class DatasetProvider:
    @staticmethod
    def load(dataset_id: str, *, split: str = "test") -> Dataset:
        from datasets import load_dataset

        return load_dataset(dataset_id, split=split)

    @staticmethod
    def image_column(dataset: Dataset) -> str:
        from datasets import Image

        for name, feature in dataset.features.items():
            if isinstance(feature, Image):
                return name

        for name in ("image", "img", "images", "pixel_values"):
            if name in dataset.column_names:
                return name

        raise ValueError(f"No image column found. Available: {dataset.column_names}")

    @staticmethod
    def label_column(dataset: Dataset) -> str:
        from datasets import ClassLabel

        for name, feature in dataset.features.items():
            if isinstance(feature, ClassLabel):
                return name

        for name in ("label", "labels", "target", "class"):
            if name in dataset.column_names:
                return name

        raise ValueError(f"No label column found. Available: {dataset.column_names}")

    @staticmethod
    def get_images(dataset: Dataset) -> Any:
        return dataset[DatasetProvider.image_column(dataset)]

    @staticmethod
    def get_labels(dataset: Dataset) -> Any:
        return dataset[DatasetProvider.label_column(dataset)]
