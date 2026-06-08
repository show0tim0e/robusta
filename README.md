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
- Python 3.10 oder neuer
- Git

### 1. Repository klonen
```bash
git clone git@git.tu-berlin.de:mva/sose_26/js2.git
cd js2
git switch dev
```

### 2. Virtuelle Umgebung erstellen
```bash
python3 -m venv .venv
```

### 3. Virtuelle Umgebung aktivieren
```bash
PowerShell: .\.venv\Scripts\Activate.ps1
cmd: .venv\Scripts\activate.bat
Linux/macOS: source .venv/bin/activate
```

### 4. Abhängigkeiten installieren
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Projekt starten
```bash
python main.py
```

## Beispiel
...

## Autoren
Miran  
Kilian  
Hassan  
Cedrik  
Tim  