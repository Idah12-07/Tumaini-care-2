# TUMAINI CARE — Symptom Triage Route
# Scores symptom inputs and returns risk level (LOW/MODERATE/HIGH/EMERGENCY)
from fastapi import APIRouter
from pydantic import BaseModel
from core.triage_engine import score_symptoms, get_risk_level

router = APIRouter()

class Symptoms(BaseModel):
    patient_id: str
    day_post_loss: int
    heavy_bleeding: bool = False
    fever: bool = False
    foul_odour: bool = False
    severe_pain: bool = False
    right_sided_pain: bool = False
    vomiting: bool = False
    dizziness: bool = False
    no_bleeding: bool = False
    raw_message: str = ''

@router.post('/score')
def score(s: Symptoms):
    score = score_symptoms(s.dict())
    level = get_risk_level(score)
    return {
        'patient_id': s.patient_id,
        'risk_score': score,
        'risk_level': level,
        'trigger_chw_alert': level in ('HIGH', 'EMERGENCY'),
        'trigger_referral': level == 'EMERGENCY'
    }
