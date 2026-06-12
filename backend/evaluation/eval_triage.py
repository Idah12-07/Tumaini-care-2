# ============================================================
# TUMAINI CARE — Triage Engine Evaluation
# Tests the deterministic risk scorer against synthetic dataset
# Target metrics:
#   - Overall accuracy > 90%
#   - Emergency false negative rate < 5%  (CRITICAL — missing emergency = harm)
#   - High false negative rate < 10%
# ============================================================
import csv
from core.triage_engine import score_symptoms, get_risk_level

def load_symptom_logs(path='data/synthetic/symptom_logs.csv'):
    with open(path) as f:
        return list(csv.DictReader(f))

def bool_field(val):
    return str(val).strip().lower() == 'true'

def evaluate_triage():
    logs = [l for l in load_symptom_logs() if l['responded'] == 'True']
    correct = 0
    false_neg_emergency = 0
    false_neg_high = 0
    total_emergency = 0
    total_high = 0

    for log in logs:
        symptoms = {
            'heavy_bleeding':   bool_field(log['heavy_bleeding']),
            'fever':            bool_field(log['fever']),
            'foul_odour':       bool_field(log['foul_odour']),
            'severe_pain':      bool_field(log['severe_pain']),
            'right_sided_pain': bool_field(log['right_sided_pain']),
            'vomiting':         bool_field(log['vomiting']),
        }
        predicted = get_risk_level(score_symptoms(symptoms))
        actual    = log['risk_level']

        if predicted == actual: correct += 1
        if actual == 'EMERGENCY':
            total_emergency += 1
            if predicted != 'EMERGENCY': false_neg_emergency += 1
        if actual == 'HIGH':
            total_high += 1
            if predicted not in ('HIGH','EMERGENCY'): false_neg_high += 1

    n = len(logs)
    print(f"\n=== TUMAINI TRIAGE EVALUATION ===")
    print(f"Total logs evaluated:       {n}")
    print(f"Overall accuracy:           {correct/n*100:.1f}%  (target: >90%)")
    print(f"Emergency false neg rate:   {false_neg_emergency/max(total_emergency,1)*100:.1f}%  (target: <5%)")
    print(f"High false neg rate:        {false_neg_high/max(total_high,1)*100:.1f}%  (target: <10%)")

if __name__ == '__main__':
    evaluate_triage()
