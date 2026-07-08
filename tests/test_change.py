from vl_scanner.core.scanner import Scanner


def test_model():
    pass

def test_dataset():
    scanner = Scanner()

    assert scanner.set_model(model_id="Ahmed9275/Vit-Cifar100")

    print("Loading CIFAR-100")
    assert scanner.set_dataset(dataset_id="uoft-cs/cifar100")

    print("Loading CIFAR-10")
    assert scanner.set_dataset(dataset_id="uoft-cs/cifar10")

    print("Loading MNIST")
    assert scanner.set_dataset(dataset_id="ylecun/mnist")

    input("Press Enter to end...")