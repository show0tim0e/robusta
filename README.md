# Development of a Framework for Vulnerability Scanning of Machine Learning and Deep Learning Models

## Description
This project aimed at implementing a Vulnerability scanner for AI/ML-Models, that evaluates the robustness of image classification models against several adversarial machine learning attacks. The Scanner automatically runs a configurable set of attacks (FGSM, PGD, TUAP) against a model and test dataset selected by the user, then quantifies the resulting damage and estimates the attacker's effort. It also provides a risk classification, providing an interpretable assessment of the model's vulnerabilities. Models are loaded via HuggingFace, and the scanner is operated through a command-line interface (CLI) driven by a TOML configuration file.

## Project Structure

The scanner is organized into four core components:

- **`core/scanner`** - central orchestrator class that coordinates the entire scan process (loading model/dataset, running attacks, collecting results)
- **`attacks/`** - attack implementations (FGSM, PGD, TUAP) built on a shared abstract base class; new attacks are registered automatically and become available system-wide without further changes
- **`core/providers/`** - loading of models (HuggingFace) and datasets; models are wrapped by an adapter to expose a unified interface
- **`assessment/`** - evaluation logic; computes damage and effort metrics from scan results and derives a risk classification
- **`cli.py`** - command-line entry point; parses the TOML config, validates it against the registered attacks, and drives the scanner and evaluator. All status output goes to stderr; results are written to a JSON file.


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
uv run robusta config.toml
```

**Run the project (CUDA 12.6, for GPU acceleration):**
```bash
uv run robusta config.toml --extra cu126
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
*(The `-e` flag installs the project in "editable" mode.)*

**Run the project:**
```bash
robusta config.toml
```
or, equivalently:
```bash
python -m robusta config.toml
```

**Run the tests:**
```bash
pytest
```
</details>

## CLI

```text
robusta [-h] [--output PATH] [--batch-size N] [--device NAME] [--quiet] CONFIG
```

Positional:
- `CONFIG` — path to a TOML configuration file (required).

Flags:
- `--output PATH` — overrides the `output` key in the TOML.
- `--batch-size N` — overrides the `batch_size` key in the TOML.
- `--device NAME` — torch device (e.g. `cpu`, `cuda`); overrides nothing (defaults to whatever `torch.cuda.is_available()` reports).
- `--quiet` — suppress progress messages on stderr (errors are still printed).

The CLI is JSON-only: status lines go to stderr and the full report is written to the path configured by `output`. Exit code `0` on success, `2` on configuration errors, `1` on runtime errors.

### Python API

The same logic is exposed as a single function for embedding in other tools:

```python
import robusta

# Returns the report dict (also writes JSON to the path configured in config.toml)
report = robusta.run(
    "config.toml",
    output="results.json",   # optional, overrides TOML
    batch_size=16,            # optional, overrides TOML
    device="cuda",            # optional, no default override
    quiet=False,              # suppress status messages on stderr
)
print(report["attacks"]["FGSM"]["scan"]["adv_accuracy"])
```

Errors are raised as `robusta.ConfigError` (a `ValueError` subclass). The exception carries an `is_config_error` flag — `True` for problems with the TOML, `False` for runtime failures (HF login, model/dataset load, file write).

### Hugging Face token

The CLI never reads a token from the config file. Set it in your environment before running:

```bash
export HF_TOKEN="hf_..."
robusta config.toml
```

To use a different env var, add `hf_token_env = "MY_TOKEN"` to the TOML.

## Notebook UI

A thin marimo notebook lives at [`notebooks/scan.py`](notebooks/scan.py) and edits `config.toml` interactively, then calls `robusta.run(...)` on click. The notebook is a single-file wrapper around the public API — no scanner, attack, or assessment logic is duplicated.

[![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/<user>/<repo>/blob/main/notebooks/scan.py)

Replace `<user>/<repo>` with the GitHub mirror of this project. In molab:

1. Open the secrets tab (�) and add `HF_TOKEN=<your-token>` — this is loaded into `os.environ` automatically.
2. Edit the TOML in the widget.
3. Click **Run scan**.

Locally:

```bash
uv run marimo edit notebooks/scan.py
```

Dependencies (`marimo`, `marimo-toml-editor`, `tomli-w`) live in `[dependency-groups].dev` and are only required for the notebook.

## Configuration schema

`config.toml` is the canonical example. The full schema:

```toml
# Required
model   = "fxmarty/resnet-tiny-mnist"   # HuggingFace model id
dataset = "ylecun/mnist"                # HuggingFace dataset id
output  = "results.json"                # where to write the JSON report

# Optional (top-level)
hf_token_env = "HF_TOKEN"               # env var name (default "HF_TOKEN")
split        = "test"                   # dataset split (default "test")
size         = 1000                     # number of samples (default: full split)
streaming    = false                    # stream from HF (default false)
batch_size   = 16                       # inference batch size (default 16)

# Attacks — one or more [attack.NAME] tables
# NAME must match a registered attack (FGSM, PGD, TUAP).
# enabled = false (or omitted → false) skips the attack.
# Other keys must match the attack's declared AttackParameter list;
# unknown attacks or unknown params are rejected at load time.

[attack.FGSM]
enabled = true
epsilon = 0.03

[attack.PGD]
enabled = false
epsilon  = 0.03
alpha    = 0.01
num_iter = 40

[attack.TUAP]
enabled       = false
target_class  = 0
eps           = 0.1
delta         = 0.2
max_iter      = 20
attacker_eps  = 0.03
```

### Report shape

`results.json` is a single object:

```json
{
  "config_path": "/abs/path/config.toml",
  "model": "...",
  "dataset": "...",
  "split": "test",
  "size": 200,
  "streaming": false,
  "batch_size": 16,
  "attacks": {
    "FGSM": {
      "params": {"epsilon": 0.03},
      "scan": {
        "clean_accuracy": 0.98,
        "adv_accuracy": 0.42,
        "avg_confidence": 0.91,
        "avg_adv_confidence": 0.63,
        "attack_time_seconds": 12.3,
        "num_samples": 200
      },
      "evaluation": {
        "attack_art": "FGSM",
        "extent_of_damage": {"composite_score": 2.31, "metrics_detail": {...}},
        "attackers_effort": {"attack_steps": 5, "attack_time_seconds": 12.3}
      }
    }
  }
}
```

## Examples

| Dataset | Model | Expected outcome |
|-|-|-|
| https://huggingface.co/datasets/ylecun/mnist | https://huggingface.co/fxmarty/resnet-tiny-mnist | Pipeline test, fast scan time but limited susceptibility to FGSM because of small number of categories, limited semantic significance |
| https://huggingface.co/datasets/uoft-cs/cifar10 | https://huggingface.co/nateraw/vit-base-patch16-224-cifar10 | Standard benchmark for adversarial robustness |
| https://huggingface.co/datasets/uoft-cs/cifar100 | https://huggingface.co/Ahmed9275/Vit-Cifar100 | More challenging benchmark with a higher misclassification rate under adversarial attacks |

The shipped `config.toml` is a CIFAR-10 example. To run it:

```bash
export HF_TOKEN="hf_..."
uv run robusta config.toml
```

## Authors
Miran Zwick  
Kilian Alexander Weise  
Hassan Hotait  
Cedrik Urbank  
Tim Leon Metz  
