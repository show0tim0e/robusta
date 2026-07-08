import shutil
from pathlib import Path

from PIL import Image
from torchvision.transforms.functional import to_pil_image

from vl_scanner.attacks.fgsm import FGSM
from vl_scanner.core.scanner import AttackConfig, Scanner


def _to_png(image, path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    tensor = image.detach().cpu().float()
    if tensor.ndim == 2:
        tensor = tensor.unsqueeze(0)
    elif tensor.ndim == 3 and tensor.shape[0] not in (1, 3, 4) and tensor.shape[-1] in (1, 3, 4):
        tensor = tensor.permute(2, 0, 1)

    base = to_pil_image(tensor.clamp(0.0, 1.0)).convert("RGB")
    Image.new("RGB", base.size, "white").paste(base)
    base.save(path)


def test_export_scan_artifacts() -> None:
    output_root = Path(__file__).resolve().parents[1] / "artifacts"
    shutil.rmtree(output_root, ignore_errors=True)

    scanner = Scanner()

    assert scanner.set_model(model_id="nateraw/vit-base-patch16-224-cifar10")
    assert scanner.set_dataset(dataset_id="uoft-cs/cifar10", size=100)

    scanner.set_attacks(
        [
            AttackConfig(
                attack=FGSM,
                params={"epsilon": 0.01})
        ]
    )

    scan = scanner.run()
    attack = scan.results[0]

    for index in range(len(scan.x)):
        sample_id = index + 1
        clean_label = int(scan.pred[index].item())
        adv_label = int(attack.adv_pred[index].item())

        if clean_label == adv_label:
            continue

        _to_png(
            scan.x[index],
            output_root / "original" / f"{sample_id}.png",
        )

        _to_png(
            attack.x_adv[index],
            output_root / "attacks" / attack.attack_name / f"{sample_id}.png",
        )

        print(
            f"{sample_id}.png: label={clean_label}, "
            f"confidence={float(scan.confidence[index].item()):.4f}, "
            f"adv_label={adv_label}, "
            f"adv_confidence={float(attack.adv_confidence[index].item()):.4f}"
        )
