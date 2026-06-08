from dataclasses import dataclass

from torch import Tensor
from torch.nn import Module

from .base import Attack


@dataclass(slots=True)
class PGD(Attack):
    def name(self) -> str:
        return "pgd"

    def generate(self, model: Module, x: Tensor, y: Tensor | None = None) -> Tensor:
        pass