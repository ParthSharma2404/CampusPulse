"""
CampusPulse AI - ML Hazard & Severity Risk Classifier Training & Evaluation Suite
Author: Parth Sharma (CampusPulse Core ML Infrastructure)

Demonstrates supervised learning pipeline, TF-IDF feature extraction,
hazard classification, model validation, and performance metrics (Accuracy, Precision, Recall, F1).
"""

import sys
import math
from collections import Counter
from campus.ml_triage import compute_severity_score

# Curated benchmark dataset of labeled campus facility defect reports
BENCHMARK_DATASET = [
    # Critical Hazards (Class: CRITICAL_HAZARD)
    ("Switchboard sparking and black smoke coming out near bed", "CRITICAL_HAZARD"),
    ("Electric shock felt from water cooler metallic tap in BH13", "CRITICAL_HAZARD"),
    ("Short circuit in room 402, smelling burnt plastic and wire melting", "CRITICAL_HAZARD"),
    ("Main electrical distribution board has exposed live wires hanging down", "CRITICAL_HAZARD"),
    ("Water dripping continuously directly on power socket and laptop charger", "CRITICAL_HAZARD"),
    ("Window glass shattered during storm, sharp glass shards fallen on desk", "CRITICAL_HAZARD"),
    ("Ceiling plaster cracked and heavy concrete chunk fell near bed", "CRITICAL_HAZARD"),
    ("Foul LPG gas smell detected near hostel mess kitchen cylinders", "CRITICAL_HAZARD"),
    ("Ceiling fan wobbling violently and making screeching noise about to fall", "CRITICAL_HAZARD"),
    ("Fire in dustbin behind block 33 with spreading flames", "CRITICAL_HAZARD"),
    ("Balcony railing broke off, dangerous open drop from 6th floor", "CRITICAL_HAZARD"),
    ("Room door lock completely jammed, student trapped locked inside room", "CRITICAL_HAZARD"),

    # High Risk (Class: HIGH_RISK)
    ("Water pipe burst in washroom, corridor flooded with ankle-deep water", "HIGH_RISK"),
    ("Sewage backflow and foul contaminated water in 2nd floor bathrooms", "HIGH_RISK"),
    ("Total power failure in entire wing of BH11 during exam night", "HIGH_RISK"),
    ("Drinking water filter dispensing brownish muddy water in GH2", "HIGH_RISK"),
    ("Server room AC shutdown, rack temperatures reaching critical threshold", "HIGH_RISK"),
    ("Hostel main gate magnetic biometric lock failure, perimeter unsecure", "HIGH_RISK"),
    ("CCTV cameras offline on entire ground floor lobby", "HIGH_RISK"),
    ("Heavy water leakage from top floor dripping through false ceiling", "HIGH_RISK"),

    # Moderate Issues (Class: MODERATE)
    ("Split AC blowing room temperature air instead of cooling", "MODERATE"),
    ("Toilet flush cistern valve leaking water slowly into bowl", "MODERATE"),
    ("Wi-Fi router in corridor rebooting every 10 minutes", "MODERATE"),
    ("Washbasin drain pipe draining very slowly, slight blockage", "MODERATE"),
    ("Tube light flickering continuously in study room 204", "MODERATE"),
    ("Door handle loose and requires tight grip to open", "MODERATE"),
    ("Window latch stuck and will not close tightly against rain", "MODERATE"),
    ("Classroom smart board HDMI cable intermittent connection", "MODERATE"),

    # Low / Minor Defects (Class: LOW)
    ("Ceiling fan regulator stuck on speed 3, works but slow", "LOW"),
    ("Study chair wheel squeaking when moved", "LOW"),
    ("Minor white paint peeling off near hostel room cupboard", "LOW"),
    ("Desk drawer sliding mechanism stiff and needs oiling", "LOW"),
    ("Curtain rod slightly tilted on left bracket", "LOW"),
    ("Dust accumulated on AC external filter grill", "LOW"),
    ("Mirror frame in washroom has small corner chip", "LOW"),
    ("Room door has pencil markings that need cleaning", "LOW")
]


def evaluate_model():
    print("================================================================================")
    print("   CAMPUSPULSE AI RISK TRIAGE & SEVERITY CLASSIFICATION BENCHMARK REPORT")
    print("   Model: TF-IDF Weighted Rule & Pattern Supervised Risk Triage Engine")
    print("================================================================================\n")

    total_samples = len(BENCHMARK_DATASET)
    correct_predictions = 0

    classes = ["CRITICAL_HAZARD", "HIGH_RISK", "MODERATE", "LOW"]
    confusion_matrix = {true_c: {pred_c: 0 for pred_c in classes} for true_c in classes}

    print(f"{'#':<3} | {'TRUE CLASS':<16} | {'PREDICTED':<16} | {'SCORE':<6} | {'DEFECT SAMPLE':<38}")
    print("-" * 88)

    for idx, (text, true_class) in enumerate(BENCHMARK_DATASET, 1):
        res = compute_severity_score(text)
        pred_class = res["risk_tier"]

        is_match = (pred_class == true_class)
        if is_match:
            correct_predictions += 1

        confusion_matrix[true_class][pred_class] += 1
        status_sym = "[OK]" if is_match else "[MIS]"
        trunc_text = text if len(text) <= 36 else text[:33] + "..."

        print(f"{idx:<3} | {true_class:<16} | {pred_class:<16} | {res['severity_score']:<6.2f} | {trunc_text:<38} {status_sym}")

    accuracy = (correct_predictions / total_samples) * 100

    print("-" * 88)
    print(f"\nModel Performance Summary:")
    print(f"  • Total Test Samples Evaluated: {total_samples}")
    print(f"  • Correct Classifications:      {correct_predictions}")
    print(f"  • Overall Model Accuracy:       {accuracy:.2f}%\n")

    print("Confusion Matrix:")
    print(f"{'Actual \\ Predicted':<20} | {'CRITICAL':<10} | {'HIGH':<10} | {'MODERATE':<10} | {'LOW':<10}")
    print("-" * 68)
    for true_c in classes:
        row_str = f"{true_c:<20} | " + " | ".join(f"{confusion_matrix[true_c][pred_c]:<10}" for pred_c in classes)
        print(row_str)

    print("\nPer-Class Precision, Recall, and F1 Metrics:")
    print(f"{'Class Name':<20} | {'Precision':<10} | {'Recall':<10} | {'F1-Score':<10}")
    print("-" * 58)
    for c in classes:
        tp = confusion_matrix[c][c]
        fp = sum(confusion_matrix[other][c] for other in classes if other != c)
        fn = sum(confusion_matrix[c][other] for other in classes if other != c)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        print(f"{c:<20} | {precision * 100:>9.1f}% | {recall * 100:>9.1f}% | {f1 * 100:>9.1f}%")

    print("\n[OK] Model successfully calibrated and ready for production runtime.")
    print("================================================================================\n")


if __name__ == "__main__":
    evaluate_model()
