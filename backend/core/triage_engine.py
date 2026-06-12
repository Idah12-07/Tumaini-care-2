# ============================================================
# TUMAINI CARE — Deterministic Symptom Triage Engine
# Based on WHO and FIGO EPL clinical danger sign guidelines
# Rule-based (not ML) for clinical transparency and auditability
# ============================================================

SYMPTOM_SCORES = {
    'heavy_bleeding':   3,   # Soaking >1 pad/hour — major haemorrhage risk
    'foul_odour':       3,   # Foul discharge — sepsis indicator
    'right_sided_pain': 3,   # One-sided pain — possible ectopic rupture
    'fever':            2,   # Temperature >38.5C — infection indicator
    'severe_pain':      2,   # Severe abdominal pain — general danger sign
    'dizziness':        2,   # Fainting/weakness — haemorrhage/shock indicator
    'vomiting':         1,   # Repeated vomiting — secondary sign
    'no_bleeding':     -1,   # Bleeding stopped — generally positive sign
}

def score_symptoms(symptoms: dict) -> int:
    '''Compute clinical risk score from symptom flags.'''
    return max(0, sum(
        SYMPTOM_SCORES.get(key, 0)
        for key, val in symptoms.items()
        if val is True and key in SYMPTOM_SCORES
    ))

def get_risk_level(score: int) -> str:
    '''Convert numeric score to clinical risk level.'''
    if score >= 5: return 'EMERGENCY'
    if score >= 3: return 'HIGH'
    if score >= 1: return 'MODERATE'
    return 'LOW'

def get_recommended_action(level: str) -> str:
    actions = {
        'LOW':       'Continue daily check-ins. Provide grief support.',
        'MODERATE':  'CHW follow-up within 24 hours. Monitor for escalation.',
        'HIGH':      'Trigger CHW alert immediately. Consider facility referral.',
        'EMERGENCY': 'EMERGENCY — CHW alert + facility referral NOW. Woman must go to hospital.',
    }
    return actions.get(level, 'Unknown')
