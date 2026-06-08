from abc import ABC, abstractmethod

from torch import Tensor
from torch.nn import Module


class Attack(ABC):
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def generate(self, model: Module, x: Tensor, y: Tensor | None = None) -> Tensor:
        pass