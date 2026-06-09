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
    @property
    @abstractmethod
    def name(self) -> str:
        """The display name of the attack."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """A detailed description of the attack."""
        pass

    @property
    @abstractmethod
    def attack_parameters(self) -> list[AttackParameter]:
        """A list of parameters for the attack, used for UI generation."""
        pass

    @abstractmethod
    def generate(self, model: Module, x: Tensor, y: Tensor, **kwargs: Any) -> Tensor:
        """
        Generates adversarial examples.
        """
        pass
