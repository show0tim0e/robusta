from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Type

from torch import Tensor
from torch.nn import Module


@dataclass(frozen=True)
class AttackParameter:
    """Defines a parameter that the UI should collect for an attack."""

    name: str
    type: Type
    default: Any = None
    optional: bool = False


class Attack(ABC):
    @staticmethod
    @abstractmethod
    def name() -> str:
        """The display name of the attack."""
        pass

    @staticmethod
    @abstractmethod
    def description() -> str:
        """A detailed description of the attack."""
        pass

    @staticmethod
    @abstractmethod
    def attack_parameters() -> list[AttackParameter]:
        """A list of parameters for the attack, used for UI generation."""
        pass

    @staticmethod
    @abstractmethod
    def generate(model: Module, x: Tensor, y: Tensor, **kwargs: Any) -> Tensor:
        """
        Generates adversarial examples.
        """
        pass
