from tests.datasets.test_mnist import _ensure_dataset_artifact
from vl_scanner.attacks.fgsm import FGSM
from vl_scanner.core.providers.dataset import DatasetProvider
from vl_scanner.core.providers.model import ModelProvider
from vl_scanner.core.scanner import AttackConfig, Scanner


def test_mnist_scan():
    model, processor = ModelProvider.load("fxmarty/resnet-tiny-mnist")

    x, y = DatasetProvider.load(_ensure_dataset_artifact())

    processor.do_rescale = False
    processor.do_normalize = True

    x = processor(
        images=x,
        return_tensors="pt"
    )["pixel_values"]

    scanner = Scanner(
        dataset=(x, y),
        model=model,
        attacks=[
            AttackConfig(attack=FGSM, params={"epsilon": 0.1}),
            #AttackConfig(attack=PGD, params={"epsilon": 0.1, "alpha": 0.01, "num_iter": 40}),
        ],
    )

    x, y,results = scanner.run()

    for result in results:
        # for i in range(len(result.x)):
        #     print(f"{result.pred[i].item()} vs {result.y[i].item()}")

        accuracy = (result.pred == y).float().mean()
        adv_accuracy = (result.adv_pred == y).float().mean()

        avg_conf = result.confidence.mean()
        avg_adv_conf = result.adv_confidence.mean()

        print(f"\nAttack: {result.attack_name}")
        print(f"Params: {result.attack_params}")
        print(f"Accuracy:      {accuracy:.2%}")
        print(f"Adv Accuracy:  {adv_accuracy:.2%}")
        print(f"Confidence:    {avg_conf:.4f}")
        print(f"Adv Confidence:{avg_adv_conf:.4f}")