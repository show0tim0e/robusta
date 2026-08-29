from pathlib import Path

from robusta.attacks.fgsm import FGSM
from robusta.core.scanner import AttackConfig, Scanner, ScanResult


def load_hf_token(path: str = ".venv.local") -> str:
    for line in Path(path).read_text().splitlines():
        line = line.strip()

        if line.startswith("HF_TOKEN="):
            return line.split("=", 1)[1].strip()

    raise ValueError("HF_TOKEN not found in .venv.local")


def process_scan_result(scan: ScanResult) -> None:
    for result in scan.results:
        accuracy = (scan.pred == scan.y).float().mean()
        adv_accuracy = (result.adv_pred == scan.y).float().mean()

        avg_conf = scan.confidence.mean()
        avg_adv_conf = result.adv_confidence.mean()

        print(f"\nAttack: {result.attack_name}")
        print(f"Params: {result.attack_params}")
        print(f"Attack Time: {result.attack_time_seconds:.2f}s")
        print(f"Accuracy:       {accuracy:.2%}")
        print(f"Adv Accuracy:   {adv_accuracy:.2%}")
        print(f"Confidence:     {avg_conf:.4f}")
        print(f"Adv Confidence: {avg_adv_conf:.4f}")


def test_set_token():
    scanner = Scanner()

    assert scanner.set_token(load_hf_token())


def test_set_dataset_streaming_requires_size():
    scanner = Scanner()

    assert not scanner.set_dataset("ylecun/mnist", streaming=True)


def test_streaming_take_sample():
    import datasets
    import PIL.Image

    from robusta.core.providers.dataset import DatasetProvider

    features = datasets.Features(
        {
            "image": datasets.Image(),
            "label": datasets.ClassLabel(names=["a", "b"]),
        }
    )
    iterable = datasets.Dataset.from_dict(
        {
            "image": [PIL.Image.new("RGB", (8, 8)) for _ in range(20)],
            "label": [i % 2 for i in range(20)],
        },
        features=features,
    ).to_iterable_dataset()

    progress = []
    images, labels = DatasetProvider.take_sample(iterable, 5, progress_callback=lambda p, m: progress.append((p, m)))

    assert len(images) == len(labels) == 5
    assert len(progress) == 5
    assert progress[-1][0] == 1.0


def test_batching():
    scanner = Scanner()

    # mnist
    # assert scanner.set_model(model_id="fxmarty/resnet-tiny-mnist")
    # assert scanner.set_dataset(dataset_id="ylecun/mnist", size=10000)

    # cifar-10
    assert scanner.set_model(model_id="nateraw/vit-base-patch16-224-cifar10")
    assert scanner.set_dataset(dataset_id="uoft-cs/cifar10", size=500)

    # cifar-100
    # assert scanner.set_model(model_id="Ahmed9275/Vit-Cifar100")
    # assert scanner.set_dataset(dataset_id="uoft-cs/cifar100", size=500)

    scanner.set_attacks(
        [
            AttackConfig(
                attack=FGSM,
                params={"epsilon": 0.03},
            )
        ]
    )

    print("Running scan with batching...")
    scan_result = scanner.run()
    process_scan_result(scan_result)

    print("\n")

    print("Running scan without batching...")
    scan_result_no_batch = scanner.run_no_batching()
    process_scan_result(scan_result_no_batch)


def test_mnist_scan():
    scanner = Scanner()

    assert scanner.set_model(model_id="fxmarty/resnet-tiny-mnist")
    assert scanner.set_dataset(dataset_id="ylecun/mnist", size=1000)

    scanner.set_attacks(
        [
            # AttackConfig(
            #     attack=TUAP,
            #     params={"targeted_class": 0, "eps": 0.1, "norm": "inf", "delta": 0.2, "max_iter": 20, "attacker": "fgsm", "attacker_eps": 0.03},
            # )
            AttackConfig(
                attack=FGSM,
                params={"epsilon": 0.03},
            )
        ]
    )

    scan_result = scanner.run()

    process_scan_result(scan_result)


def test_cifar10_scan():
    scanner = Scanner()

    assert scanner.set_model(model_id="nateraw/vit-base-patch16-224-cifar10")
    assert scanner.set_dataset(dataset_id="uoft-cs/cifar10", size=200)

    scanner.set_attacks(
        [
            AttackConfig(
                attack=FGSM,
                params={"epsilon": 0.03},
            )
        ]
    )

    scan_result = scanner.run()

    process_scan_result(scan_result)


def test_cifar100_scan():
    scanner = Scanner()

    assert scanner.set_model(model_id="Ahmed9275/Vit-Cifar100")
    assert scanner.set_dataset(dataset_id="uoft-cs/cifar100", size=200)

    scanner.set_attacks(
        [
            AttackConfig(
                attack=FGSM,
                params={"epsilon": 0.03},
            )
        ]
    )

    scan_result = scanner.run()

    process_scan_result(scan_result)
