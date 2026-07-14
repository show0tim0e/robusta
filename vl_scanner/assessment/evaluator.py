from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vl_scanner.core.scanner import AttackResult, ScanResult


class Evaluator:
    def __init__(self):
        # Our lookup table to define attack steps for measuring effort
        self.attack_profiles = {
            "fgsm": 5,  # Example values for our attacks
            "pgd": 8,
            "tuap": 12
        }

    
    def evaluate(self, scan_result: ScanResult, progress_callback=None) -> dict:
        import numpy as np
        from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

        y_true = scan_result.y.numpy()  # True labels converted to numerical values
        y_pred_orig = scan_result.pred.numpy()  # Predicted labels before the attack
        probs_orig = scan_result.confidence.numpy()  # Confidence scores of the predicted labels

        # Create a mask with all correctly classified instances to artificially test a "perfect model"
        correct_mask = (y_pred_orig == y_true) 
        
        y_true_filt = y_true[correct_mask]  # Only the correctly predicted labels
        probs_orig_filt = probs_orig[correct_mask]  # Confidence scores of only the correctly predicted labels

        evaluation_results = {}

        attack_res: AttackResult  # Type hint
        total = len(scan_result.results)

        # If multiple attacks are evaluated, iterate through all of them using a for loop
        for i, attack_res in enumerate(scan_result.results): 
            attack_name = attack_res.attack_name
            attack_time_seconds = attack_res.attack_time_seconds
            
            # Retrieve labels and confidence AFTER the attack
            y_pred_adv = attack_res.adv_pred.numpy()  # Labels
            probs_adv = attack_res.adv_confidence.numpy()  # Confidence
            
            # Apply the mask to both
            y_pred_adv_filt = y_pred_adv[correct_mask]
            probs_adv_filt = probs_adv[correct_mask]

            # If the list is empty after filtering (Safety check)
            if len(y_true_filt) == 0:
                print(f"Warning: The model did not correctly recognize a single image before the attack '{attack_name}'. Skipping...")
                continue

            # Calculate base metrics using imported functions
            acc = accuracy_score(y_true_filt, y_pred_adv_filt)
            prec = precision_score(y_true_filt, y_pred_adv_filt, average='macro', zero_division=0)
            rec = recall_score(y_true_filt, y_pred_adv_filt, average='macro', zero_division=0)
            f1 = f1_score(y_true_filt, y_pred_adv_filt, average='macro', zero_division=0)
            
            # Invert the metrics to convert from 'accuracy/success' to 'damage'
            inv_acc, inv_prec, inv_rec, inv_f1 = 1.0 - acc, 1.0 - prec, 1.0 - rec, 1.0 - f1
            composite_damage = inv_acc + inv_prec + inv_rec + inv_f1  # Total composite damage (max 4.0)
            
            # Calculate the average confidence drop and cast to float
            conf_drop = float(np.mean(probs_orig_filt - probs_adv_filt))  

            # Retrieve the steps locally, 0 as fallback if a name is misspelled
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

        return evaluation_results  # Nested dictionary mapped by attack names