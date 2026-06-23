# Entwicklung eines Frameworks für Vulnerability Scans auf Machine Learning und Deep Learning Modelle

## Beschreibung
VL Scanner ist ein modulares System für die Analyse der Robustheit von PyTorch-Modellen gegenüber adversarial attacks im Bereich Bildklassifikation.

## Projektstruktur
TODO

## Installation
### Voraussetzungen
- Python 3.12 oder neuer
- Git

### 1. Repository klonen
```bash
git clone git@git.tu-berlin.de:mva/sose_26/js2.git
cd js2
git switch dev
```

### 2. Projekt ausführen & testen

<details>
<summary><b>Verwendung mit uv (empfohlen)</b></summary>

[uv](https://docs.astral.sh/uv/) ist ein extrem schneller Python-Paketmanager. Bei Verwendung von `uv run` wird die Umgebung automatisch synchronisiert.

**Projekt starten:**
```bash
uv run main.py
```

**Tests ausführen:**
```bash
uv run pytest
```
</details>

<details>
<summary><b>Verwendung mit pip</b></summary>

**Virtuelle Umgebung erstellen:**
```bash
python3 -m venv .venv
```

**Virtuelle Umgebung aktivieren:**
- **Linux/macOS:** `source .venv/bin/activate`
- **Windows PowerShell:** `.\.venv\Scripts\Activate.ps1`
- **Windows cmd:** `.venv\Scripts\activate.bat`

**Abhängigkeiten installieren:**
```bash
pip install -e .
```
*(Das `-e` Flag installiert das Projekt im "editable" Modus.)*

**Projekt starten:**
```bash
python main.py
```

**Tests ausführen:**
```bash
pytest
```
</details>

## Beispiele

| Dataset | Modell | Erwartung |
|-|-|-|
| https://huggingface.co/datasets/ylecun/mnist | https://huggingface.co/fxmarty/resnet-tiny-mnist | Pipeline-Test, sehr hohe FGSM/PGD Anfälligkeit, eingeschränkte semantische Aussagekraft |
| CIFAR-10 | https://huggingface.co/nateraw/vit-base-patch16-224-cifar10 | Standard Benchmark für adversarial robustness |
| CIFAR-100 | https://huggingface.co/Ahmed9275/Vit-Cifar100 | Schwieriger Benchmark mit höherer Fehlklassifikationsrate unter Angriffen |

## Autoren
Miran  
Kilian  
Hassan  
Cedrik  
Tim  