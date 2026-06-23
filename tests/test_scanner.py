import torch

from vl_scanner.attacks.fgsm import FGSM
from vl_scanner.core.providers.dataset import DatasetProvider
from vl_scanner.core.providers.model import ModelProvider
from vl_scanner.core.scanner import AttackConfig, Scanner, ScanResult


def conduct_scan(
        model_id: str,
        dataset_id: str,
        size: int,
        attacks: list[AttackConfig]
) -> ScanResult:
    
    model, processor = ModelProvider.load(model_id=model_id)

    dataset = DatasetProvider.load(dataset_id=dataset_id)

    dataset = dataset.select(range(size))

    images = DatasetProvider.get_images(dataset)
    labels = DatasetProvider.get_labels(dataset)

    encoded = processor(
        images=list(images),
        return_tensors="pt",
        do_normalize=True,
    )

    x = encoded["pixel_values"]
    y = torch.tensor(list(labels))

    scanner = Scanner(
        dataset=(x, y),
        model=model,
        attacks=attacks
    )

    return scanner.run()

def process_scan_result(scan: ScanResult) -> None:
    for result in scan.results:
        accuracy = (scan.pred == scan.y).float().mean()
        adv_accuracy = (result.adv_pred == scan.y).float().mean()

        avg_conf = scan.confidence.mean()
        avg_adv_conf = result.adv_confidence.mean()

        print(f"\nAttack: {result.attack_name}")
        print(f"Params: {result.attack_params}")
        print(f"Accuracy:       {accuracy:.2%}")
        print(f"Adv Accuracy:   {adv_accuracy:.2%}")
        print(f"Confidence:     {avg_conf:.4f}")
        print(f"Adv Confidence: {avg_adv_conf:.4f}")

def test_mnist_scan():
    scan_result = conduct_scan(
        model_id="fxmarty/resnet-tiny-mnist",
        dataset_id="ylecun/mnist",
        size=5000,
        attacks=[
            AttackConfig(
                attack=FGSM,
                params={"epsilon": 0.1},
            )
        ]
    )

    process_scan_result(scan_result)

def test_cifar10_scan():
    scan_result = conduct_scan(
        model_id="nateraw/vit-base-patch16-224-cifar10",
        dataset_id="uoft-cs/cifar10",
        size=100,
        attacks=[
            AttackConfig(
                attack=FGSM,
                params={"epsilon": 0.03},
            )
        ]
    )
    
    process_scan_result(scan_result)

def test_cifar100_scan():
    scan_result = conduct_scan(
        model_id="Ahmed9275/Vit-Cifar100",
        dataset_id="",
        size=15,
        attacks=[
            AttackConfig(
                attack=FGSM,
                params={"epsilon": 0.03},
            )
        ]
    )

    process_scan_result(scan_result)