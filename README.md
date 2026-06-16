# Entwicklung eines Frameworks für Vulnerability Scans auf Machine Learning und Deep Learning Modelle

## Beschreibung
VL Scanner ist ein modulares System für die Analyse der Robustheit von PyTorch-Modellen gegenüber adversarial attacks im Bereich Bildklassifikation.

## Projektstruktur
```text
vl_scanner/
├── core/
│   ├── model.py
│   ├── dataset.py
│   └── scanner.py
├── assessment/
│   ├── evaluator.py
│   └── report.py
├── attacks/
	├── base.py
	├── fgsm.py
	└── pgd.py
└── ui/
	└── app.py
```

## Installation
### Voraussetzungen
- Python 3.13 oder neuer
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
| MNIST | ResNet18 (ImageNet-pretrained, 1-Kanal adaptiert, 10 Klassen) | Pipeline-Test, sehr hohe FGSM/PGD Anfälligkeit, eingeschränkte semantische Aussagekraft |
| CIFAR-10 | ResNet18 (ImageNet-pretrained, 3-Kanal, 10 Klassen) | Standard Benchmark für adversarial robustness |
| CIFAR-100 | ResNet18 (ImageNet-pretrained, 3-Kanal, 100 Klassen) | Schwieriger Benchmark mit höherer Fehlklassifikationsrate unter Angriffen |

> Hinweis: Alle Modelle nutzen denselben ResNet18 Backbone mit ImageNet-pretrained Gewichten. Unterschiede ergeben sich ausschließlich durch Input-Adaptation und die finale Klassifikationsschicht.

## Autoren
Miran  
Kilian  
Hassan  
Cedrik  
Tim  