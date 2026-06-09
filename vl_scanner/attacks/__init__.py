from .base import Attack, AttackParameter
from .fgsm import FGSM
from .pgd import PGD

ATTACK_REGISTRY: dict[str, type[Attack]] = {
    attack.name(): attack for attack in [FGSM, PGD]
}

__all__ = ["Attack", "AttackParameter", "FGSM", "PGD", "ATTACK_REGISTRY"]
