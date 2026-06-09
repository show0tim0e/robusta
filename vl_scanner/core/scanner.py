from dataclasses import dataclass, field
from typing import Sequence

from vl_scanner.attacks.base import Attack

from .dataset import Dataset
from .model import Model


@dataclass(slots=True)
class Scanner:
    model: Model
    dataset: Dataset
    attacks: Sequence[type[Attack]] = field(default_factory=tuple)

    def run(self) -> dict[str, float]:
        pass