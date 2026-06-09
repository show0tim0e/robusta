from dataclasses import dataclass
from typing import Any

from torch import Tensor
from torch.nn import Module

from .base import Attack


@dataclass(slots=True)
class FGSM(Attack):
    def name(self) -> str:
        return "fgsm"
    
    def get_params(self) -> dict[str,Any]:
        pass

    def generate(self, model: Module, x: Tensor, y: Tensor, params: dict[str,Any]) -> Tensor:
        pass