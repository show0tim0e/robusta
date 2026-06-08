from dataclasses import dataclass

from torch import Tensor
from torch.nn import Module

from .base import Attack


@dataclass(slots=True)
class FGSM(Attack):
    def name(self) -> str:
        return "fgsm"

    def generate(self, model: Module, x: Tensor, y: Tensor | None = None) -> Tensor:
        pass