from abc import ABC, abstractmethod
from typing import Any

from torch import Tensor
from torch.nn import Module


class Attack(ABC):
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def get_params(self) -> dict[str,Any]:
        pass

    @abstractmethod
    def generate(self, model: Module, x: Tensor, y: Tensor, params: dict[str,Any]) -> Tensor:
        pass