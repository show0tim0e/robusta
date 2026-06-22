

from tests.datasets.test_mnist import _ensure_dataset_artifact
from tests.models.test_resnet18_mnist import _ensure_model_checkpoint
from vl_scanner.attacks.fgsm import FGSM
from vl_scanner.attacks.pgd import PGD
from vl_scanner.core.providers.dataset import DatasetProvider
from vl_scanner.core.providers.model import ModelProvider
from vl_scanner.core.scanner import AttackConfig, Scanner


def test_resnet18_mnist_scan():
    scanner = Scanner(
        dataset=DatasetProvider.load(_ensure_dataset_artifact()),
        model=ModelProvider.load(_ensure_model_checkpoint()),
        attacks=[
            AttackConfig(attack=FGSM, params={"epsilon": 0.03}),
            AttackConfig(attack=PGD, params={"epsilon": 0.03, "alpha": 0.01, "num_iter": 40}),
        ],
    )

    results = scanner.run()

    for result in results:
        accuracy = (result.pred == result.y).float().mean()
        adv_accuracy = (result.adv_pred == result.y).float().mean()

        avg_conf = result.confidence.mean()
        avg_adv_conf = result.adv_confidence.mean()

        print(f"\nAttack: {result.attack_name}")
        print(f"Accuracy:      {accuracy:.2%}")
        print(f"Adv Accuracy:  {adv_accuracy:.2%}")
        print(f"Confidence:    {avg_conf:.4f}")
        print(f"Adv Confidence:{avg_adv_conf:.4f}")