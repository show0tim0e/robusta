from collections.abc import Sequence
from dataclasses import dataclass, field

from torch import Tensor
from torch.nn import Module

from vl_scanner.attacks.base import Attack


@dataclass(slots=True)
class Scanner:
    model: Module
    dataset: tuple[Tensor, Tensor]
    attacks: Sequence[type[Attack]] = field(default_factory=tuple)

    def run(self) -> None:
        pass
