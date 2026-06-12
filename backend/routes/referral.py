"""
TUMAINI CARE — Referral Document Generator
Auto-generates a structured referral document when a woman
needs to be sent to a health facility.
Sent as: formatted text via SMS, or downloadable via dashboard.
"""
from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

router = APIRouter()


class ReferralRequest(BaseModel):
    patient_id:      str
    first_name:      str
    age:             int
    county:          str
    epl_type:        str
    date_of_loss:    str
    day_post_loss:   int
    risk_level:      str
    risk_score:      int
    symptoms:        List[str]     # list of active symptom names
    chw_id:          str
    chw_visited:     bool = False
    chw_notes:       str = ""
    facility_name:   str = "Nearest Health Facility"
    language_pref:   str = "Swahili"


SYMPTOM_LABELS = {
    "heavy_bleeding":   "Heavy bleeding (damu nyingi)",
    "fever":            "Fever / high temperature (homa kali)",
    "foul_odour":       "Foul-smelling discharge (harufu mbaya)",
    "severe_pain":      "Severe abdominal pain (maumivu makali)",
    "right_sided_pain": "Right-sided pain - possible ectopic (maumivu upande wa kulia)",
    "dizziness":        "Dizziness / weakness (kizunguzungu)",
    "vomiting":         "Vomiting (kutapika)",
}

RISK_ACTIONS = {
    "HIGH":      "Urgent assessment required within 2 hours",
    "EMERGENCY": "EMERGENCY — Immediate assessment on arrival. Do not delay.",
    "MODERATE":  "Assessment required today",
}


@router.post("/generate")
def generate_referral(req: ReferralRequest):
    """
    Generate a structured referral document.
    Returns both a plain-text version (for SMS) and
    a structured JSON version (for dashboard display).
    """
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    symptom_list = [
        SYMPTOM_LABELS.get(s, s) for s in req.symptoms
    ]
    action = RISK_ACTIONS.get(req.risk_level, "Assessment required")

    # ── Plain text version (for SMS to facility) ─────────────
    sms_text = (
        f"TUMAINI REFERRAL | {now}\n"
        f"Patient: {req.first_name}, Age {req.age}, {req.county}\n"
        f"EPL: {req.epl_type}\n"
        f"Days since loss: {req.day_post_loss}\n"
        f"Risk: {req.risk_level} (score {req.risk_score})\n"
        f"Symptoms: {', '.join(symptom_list) or 'See notes'}\n"
        f"CHW visited: {'Yes' if req.chw_visited else 'No'}\n"
        f"Action: {action}\n"
        f"Lang pref: {req.language_pref}\n"
        f"Ref: {req.patient_id}"
    )

    # ── Structured version (for dashboard) ───────────────────
    structured = {
        "document_type":    "POST-EPL REFERRAL — TUMAINI CARE",
        "generated_at":     now,
        "reference_id":     f"REF-{req.patient_id}-{datetime.utcnow().strftime('%Y%m%d%H%M')}",
        "receiving_facility": req.facility_name,
        "patient": {
            "id":              req.patient_id,
            "name":            req.first_name,
            "age":             req.age,
            "county":          req.county,
            "language_pref":   req.language_pref,
        },
        "clinical": {
            "epl_type":        req.epl_type,
            "date_of_loss":    req.date_of_loss,
            "day_post_loss":   req.day_post_loss,
            "risk_level":      req.risk_level,
            "risk_score":      req.risk_score,
            "active_symptoms": symptom_list,
        },
        "chw": {
            "chw_id":          req.chw_id,
            "visited":         req.chw_visited,
            "notes":           req.chw_notes or "No notes recorded",
        },
        "action_required":   action,
        "note": (
            "Pre-populated by Tumaini AI community surveillance system. "
            "Verify all details with patient on arrival. "
            "Do not delay care pending verification."
        ),
        "sms_version":      sms_text,
    }

    return structured


@router.get("/sample")
def sample_referral():
    """Returns a sample referral for demo purposes."""
    sample = ReferralRequest(
        patient_id="TUM0001",
        first_name="Auma",
        age=28,
        county="Kisumu",
        epl_type="Spontaneous miscarriage (incomplete)",
        date_of_loss="2026-04-28",
        day_post_loss=5,
        risk_level="EMERGENCY",
        risk_score=8,
        symptoms=["heavy_bleeding", "fever", "foul_odour"],
        chw_id="CHW001",
        chw_visited=True,
        chw_notes="Patient found at home, very weak, husband present",
        facility_name="Kisumu County Referral Hospital",
        language_pref="Swahili",
    )
    return generate_referral(sample)