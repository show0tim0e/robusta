# Development of a Framework for Vulnerability Scanning of Machine Learning and Deep Learning Models

## Description
This project aimed at implementing a Vulnerability scanner for AI/ML-Models, that evaluates the robustness of image classification models against several adversarial machine learning attacks. The Scanner automatically runs a configurable set of attacks (FGSM, PGD, TUAP) against a model and test dataset selected by the user, then quantifies the resulting damage and estimates the attacker's effort. It also provides a risk classification, providing an interpretable assessment of the model's vulnerabilities. Models are loaded via HuggingFace, and the scanner is operated through a terminal user interface (TUI).

## Project Structure

The scanner is organized into five core components:

- **`core/scanner`** - central orchestrator class that coordinates the entire scan process (loading model/dataset, running attacks, collecting results)
- **`attacks/`** - attack implementations (FGSM, PGD, TUAP) built on a shared abstract base class; new attacks are registered automatically and become available system-wide without further changes
- **`core/providers/`** - loading of models (HuggingFace) and datasets; models are wrapped by an adapter to expose a unified interface
- **`assessment/`** - evaluation logic; computes damage and effort metrics from scan results and derives a risk classification
- **`ui/`** - terminal user interface, communicates exclusively with the scanner and has no direct access to the underlying components


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

**Run the project (CPU):**
```bash
uv run main.py
```

**Run the project (CUDA 12.6, for GPU acceleration):**
```bash
uv run main.py --extra cu126
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
| https://huggingface.co/datasets/ylecun/mnist | https://huggingface.co/fxmarty/resnet-tiny-mnist | Pipeline test, fast scan time but limited susceptibility to FGSM because of small number of categories, limited semantic significance |
| https://huggingface.co/datasets/uoft-cs/cifar10 | https://huggingface.co/nateraw/vit-base-patch16-224-cifar10 | Standard benchmark for adversarial robustness |
| https://huggingface.co/datasets/uoft-cs/cifar100 | https://huggingface.co/Ahmed9275/Vit-Cifar100 | More challenging benchmark with a higher misclassification rate under adversarial attacks |

## Authors
Miran Zwick  
Kilian Alexander Weise  
Hassan Hotait  
Cedrik Urbank  
Tim Leon Metz  