from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vl_scanner.core.scanner import AttackResult, ScanResult


class Evaluator:
    def __init__(self):
        #unsere Lookup Tabelle um attack steps zu definieren für Aufwand
        self.attack_profiles = {
            "fgsm": 5,    # Beispielwerte für unsere Angriffe
            "pgd": 8,
            "tuap": 12
        }

    def evaluate(self, scan_result: ScanResult, progress_callback=None) -> dict:
        import numpy as np
        from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

        y_true = scan_result.y.numpy() # in Zahlenwerte die wahrenLabes
        y_pred_orig = scan_result.pred.numpy() # vor Angriff labels
        probs_orig = scan_result.confidence.numpy() #Konfidenz der vorhergesagten Labels

        correct_mask = (y_pred_orig == y_true) # erstellen maske mit allen richtig gelabelten vom Modell, sodass wir künstlich ein "perfektes Modell" teste
        y_true_filt = y_true[correct_mask] # nur richtig geratenen
        probs_orig_filt = probs_orig[correct_mask] # Confidence von nur richtig geratenen

        evaluation_results = {}

        attack_res: AttackResult #Typehint
        total = len(scan_result.results)

        for i, attack_res in enumerate(scan_result.results): #falls man mehrere angriffe bewertet, dann mit for schleife alle durch
            attack_name = attack_res.attack_name
            attack_time_seconds = attack_res.attack_time_seconds
            #wir holen labelung und Konfidenz NACH Angriff
            y_pred_adv = attack_res.adv_pred.numpy() #Labelung
            probs_adv = attack_res.adv_confidence.numpy() # Konfidenz
            #Maske anwenden auf beide
            y_pred_adv_filt = y_pred_adv[correct_mask]
            probs_adv_filt = probs_adv[correct_mask]

            # Wenn die Liste nach dem Filtern leer ist (Sicherheits-Check)
            if len(y_true_filt) == 0:
                print(f"Warnung: Modell hat vor dem Angriff '{attack_name}' kein einziges Bild richtig erkannt. Überspringe...")
                continue

            #Basis-Metriken berechnen per importierte Func
            acc = accuracy_score(y_true_filt, y_pred_adv_filt)
            prec = precision_score(y_true_filt, y_pred_adv_filt, average='macro', zero_division=0)
            rec = recall_score(y_true_filt, y_pred_adv_filt, average='macro', zero_division=0)
            f1 = f1_score(y_true_filt, y_pred_adv_filt, average='macro', zero_division=0)
            #invertierung der Metriken um von Accuracy zu schaden zu schaden
            inv_acc, inv_prec, inv_rec, inv_f1 = 1.0 - acc, 1.0 - prec, 1.0 - rec, 1.0 - f1
            composite_damage = inv_acc + inv_prec + inv_rec + inv_f1 #insgesamter damage max. 4
            conf_drop = float(np.mean(probs_orig_filt - probs_adv_filt)) #durchnitt des confidenzdrops berechnen und auf float ändern

            # Holt die Steps lokal, 0 als Fallback wenn ein Name falsch geschrieben wurde
            attack_steps = self.attack_profiles.get(attack_name.lower(), 0)

            evaluation_results[attack_name] = {
                "attack_art": attack_name,
                "extent_of_damage": {
                    "composite_score": composite_damage,
                    "metrics_detail": {
                        "inverted_accuracy": inv_acc,
                        "inverted_macro_precision": inv_prec,
                        "inverted_macro_recall": inv_rec,
                        "inverted_macro_f1": inv_f1,
                        "average_confidence_drop": conf_drop
                    }
                },
                "attackers_effort": {
                    "attack_steps": attack_steps,
                    "attack_time_seconds": attack_time_seconds
                }
            }

            if progress_callback is not None:
                progress = (i + 1) / total if total > 0 else 1.0
                progress_callback(progress, f"Evaluating attack: {attack_name}")

        return evaluation_results #verschactelter dictianory nach angriffsnamen
