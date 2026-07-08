from .base import Attack, AttackParameter

__all__ = ["Attack", "AttackParameter", "FGSM", "PGD", "TUAP"]

_LOADED = False


def ensure_loaded() -> None:
    """Import concrete attack modules so they register in Attack.registry
    and become available as ``vl_scanner.attacks.FGSM`` etc."""
    global _LOADED
    if _LOADED:
        return
    from . import fgsm, pgd, tuap
    globals()["FGSM"] = fgsm.FGSM
    globals()["PGD"] = pgd.PGD
    globals()["TUAP"] = tuap.TUAP
    _LOADED = True


def __getattr__(name: str):
    if name in ("FGSM", "PGD", "TUAP"):
        ensure_loaded()
        value = globals().get(name)
        if value is not None:
            return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
