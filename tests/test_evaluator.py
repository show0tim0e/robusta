import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from pathlib import Path

from vl_scanner.assessment.evaluator import Evaluator
from vl_scanner.attacks.fgsm import FGSM
from vl_scanner.core.scanner import AttackConfig, Scanner


def load_hf_token(path: str = ".venv.local") -> str:
    """Lädt das Hugging Face Token aus der versteckten lokalen Datei."""
    try:
        for line in Path(path).read_text().splitlines():
            line = line.strip()
            if line.startswith("HF_TOKEN="):
                return line.split("=", 1)[1].strip()
        raise ValueError("HF_TOKEN nicht in .venv.local gefunden.")
    except FileNotFoundError:
        raise FileNotFoundError("Die Datei .venv.local existiert nicht im Hauptverzeichnis!")

def test_evaluator_integration():
    print("\n" + "="*50)
    print("🚀 STARTE EVALUATOR SMOKE TEST (5 Bilder)")
    print("="*50)
    
    scanner = Scanner()

    # 1. Login (Token laden)
    try:
        token = load_hf_token()
        scanner.set_token(token)
        print("[OK] Hugging Face Token erfolgreich geladen.")
    except Exception as e:
        print(f"[FEHLER] Token-Problem: {e}")
        return

    # 2. Modell und Datensatz laden (Wir nehmen CIFAR10, wie Ihre Kollegen)
    print("⏳ Lade KI-Modell und Datensatz (das kann beim ersten Mal kurz dauern)...")
    modell_ok = scanner.set_model(model_id="nateraw/vit-base-patch16-224-cifar10")
    daten_ok = scanner.set_dataset(dataset_id="uoft-cs/cifar10", size=5) # Nur 5 Bilder!
    
    if not (modell_ok and daten_ok):
        print("[FEHLER] Modell oder Datensatz konnten nicht geladen werden.")
        return
        
    print("[OK] Modell und Daten geladen.")

    # 3. Angriff konfigurieren (Wir nehmen das schnelle FGSM)
    print("⚔️  Konfiguriere FGSM Angriff...")
    scanner.set_attacks([
        AttackConfig(
            attack=FGSM,
            params={"epsilon": 0.03},
        )
    ])

    # 4. Scanner ausführen
    print("⏳ Scanner jagt die 5 Bilder durch die Grafikkarte...")
    scan_result = scanner.run()
    print("[OK] Scanner fertig! Ergebnisse liegen vor.")

    # 5. Unseren Evaluator testen!
    print("🧮 Übergebe Daten an Ihren Evaluator zur Berechnung...")
    evaluator = Evaluator()
    evaluation_results = evaluator.evaluate(scan_result)

    # 6. Schöne JSON Ausgabe
    print("\n" + "🌟 TEST ERFOLGREICH! HIER IST IHR JSON-ERGEBNIS 🌟")
    print("="*50)
    print(json.dumps(evaluation_results, indent=4))
    print("="*50 + "\n")

if __name__ == "__main__":
    test_evaluator_integration()