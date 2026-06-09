from vl_scanner.attacks.fgsm import FGSM
from vl_scanner.attacks.pgd import PGD

def main() -> int:
    from vl_scanner.ui.app import run_app

    attack_registry = [FGSM(), PGD()]

    return run_app()


if __name__ == "__main__":
    raise SystemExit(main())