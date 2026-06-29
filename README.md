# Development of a Framework for Vulnerability Scanning of Machine Learning and Deep Learning Models

## Description
VL Scanner is a modular framework for analyzing the robustness of PyTorch models against adversarial attacks in the field of image classification.

## Project structure
TODO

## Installation
### Prerequisites
- Python 3.12 or later
- Git

### 1. Clone repository
```bash
git clone git@git.tu-berlin.de:mva/sose_26/js2.git
cd js2
git switch dev
```

### 2. Run and test the project

<details>
<summary><b>Using uv (recommended)</b></summary>

[uv](https://docs.astral.sh/uv/) is an extremely fast Python package manager. When using uv run, the environment is synchronized automatically.

**Run the project:**
```bash
uv run main.py
```

**Run the tests:**
```bash
uv run pytest
```
</details>

<details>
<summary><b>Using pip</b></summary>

**Create a virtual environment:**
```bash
python3 -m venv .venv
```

**Activate the virtual environment:**
- **Linux/macOS:** `source .venv/bin/activate`
- **Windows PowerShell:** `.\.venv\Scripts\Activate.ps1`
- **Windows cmd:** `.venv\Scripts\activate.bat`

**Install the dependencies:**
```bash
pip install -e .
```
*(The `-e` flag installs the project in "ediatable" mode.)*

**Run the project:**
```bash
python main.py
```

**Run the tests:**
```bash
pytest
```
</details>

## Examples

| Dataset | Model | Expected outcome |
|-|-|-|
| https://huggingface.co/datasets/ylecun/mnist | https://huggingface.co/fxmarty/resnet-tiny-mnist | Pipeline test, very high susceptibility to FGSM/PGD attacks, limited semantic significance |
| https://huggingface.co/datasets/uoft-cs/cifar10 | https://huggingface.co/nateraw/vit-base-patch16-224-cifar10 | Standard benchmark for adversarial robustness |
| https://huggingface.co/datasets/uoft-cs/cifar100 | https://huggingface.co/Ahmed9275/Vit-Cifar100 | More challenging benchmark with a higher misclassification rate under adversarial attacks |

## Authors
Miran  
Kilian  
Hassan  
Cedrik  
Tim  