from collections.abc import Callable

from torch.nn import Module

ModelBuilder = Callable[
    [int, int],
    Module,
]


class ModelRegistry:

    _builders: dict[str, ModelBuilder] = {}


    @classmethod
    def register(
        cls,
        architecture: str,
        builder: ModelBuilder,
    ) -> None:

        cls._builders[
            architecture.lower()
        ] = builder


    @classmethod
    def create(
        cls,
        architecture: str,
        num_classes: int,
        input_channels: int,
    ) -> Module:

        name = architecture.lower()

        if name not in cls._builders:
            raise KeyError(
                f"Unknown architecture: {name}"
            )

        return cls._builders[name](
            num_classes,
            input_channels,
        )