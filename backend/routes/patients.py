# Patients Route — enrol, list, get patient detail
"""
TUMAINI CARE — Patients Route
Enrol women, retrieve patient detail, list enrolled patients.
"""
from datetime import datetime, date as date_cls
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional, List

from core.database import get_db
from models.patient import Patient

router = APIRouter()


# ── Schemas ───────────────────────────────────────────────────────────────────

class PatientEnrol(BaseModel):
    phone_number:          str            # will be hashed immediately
    first_name:            str
    last_name_initial:     str
    age:                   int
    county:                str
    sub_county:            Optional[str] = None
    rural:                 bool = True
    epl_type:              str
    gestational_age_weeks: Optional[int] = None
    date_of_loss:          str            # YYYY-MM-DD
    parity:                int = 0
    prior_losses:          int = 0
    facility_of_diagnosis: Optional[str] = None
    channel:               str = "WhatsApp"
    language_pref:         str = "Swahili"
    chw_id:                Optional[str] = None
    consent_given:         bool = False


class PatientOut(BaseModel):
    patient_id:            str
    first_name:            str
    age:                   int
    county:                str
    epl_type:              str
    date_of_loss:          str
    channel:               str
    language_pref:         str
    chw_id:                Optional[str]
    enrolled_at:           str
    active:                bool
    day_post_loss_today:   int


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/enrol", response_model=PatientOut, status_code=201)
def enrol_patient(data: PatientEnrol, db: Session = Depends(get_db)):
    """
    Enrol a woman into Tumaini post-EPL monitoring.
    Called at facility discharge or by CHW during community visit.
    Phone number is hashed immediately — never stored in plain text.
    """
    if not data.consent_given:
        raise HTTPException(status_code=400, detail="Informed consent is required before enrolment.")

    # Check not already enrolled (same phone hash)
    phone_hash = Patient.hash_phone(data.phone_number)
    existing = db.query(Patient).filter(Patient.phone_hash == phone_hash).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Patient already enrolled as {existing.patient_id}")

    # Generate patient ID
    count = db.query(Patient).count()
    patient_id = f"TUM{str(count + 1).zfill(4)}"

    # Parse EPL type safely
    try:
        epl = data.epl_type
    except ValueError:
        epl = "spontaneous_incomplete"   # safe default

    patient = Patient(
        patient_id            = patient_id,
        phone_hash            = phone_hash,
        first_name            = data.first_name.strip().title(),
        last_name_init        = data.last_name_initial.strip().upper()[0],
        age                   = data.age,
        county                = data.county.strip().title(),
        sub_county            = data.sub_county,
        rural                 = data.rural,
        epl_type              = epl,
        gestational_age_weeks = data.gestational_age_weeks,
        date_of_loss          = date_cls.fromisoformat(data.date_of_loss),
        parity                = data.parity,
        prior_losses          = data.prior_losses,
        facility_of_diagnosis = data.facility_of_diagnosis,
        channel               = data.channel,
        language_pref         = data.language_pref,
        chw_id                = data.chw_id,
        consent_given         = data.consent_given,
        enrolled              = True,
        active                = True,
        enrolled_at           = datetime.utcnow(),
    )

    db.add(patient)
    db.commit()
    db.refresh(patient)
    # Send welcome/check-in SMS if enrolled via SMS channel
    from routes.sms import send_sms

    days_since = (date_cls.today() - patient.date_of_loss).days

    if patient.language_pref in ("Swahili", "Swahili+dialect", "Swahili+English mix"):
        welcome = (
            f"Habari {patient.first_name}. Mimi ni Tumaini — "
            f"nitakuwa nawe katika siku hizi ngumu. "
            f"Utapokea ujumbe kila siku kwa siku 14. "
            f"Piga *384# wakati wowote au jibu ujumbe huu. "
            f"Jibu STOP kukomesha."
        )
    else:
        welcome = (
            f"Hello {patient.first_name}. I am Tumaini — "
            f"I will be with you through these difficult days. "
            f"You will receive a daily check-in for 14 days. "
            f"Dial *384*4993# anytime or reply to this message. "
            f"Reply STOP to unsubscribe."
        )

    # Send via chosen channel
    if patient.channel == "SMS" and patient.phone_hash:
        send_sms(f"+{patient.phone_hash[:12]}", welcome)

    return _to_out(patient)


@router.get("/list")
def list_patients(db: Session = Depends(get_db)):
    patients = db.query(Patient).filter(Patient.active == True).all()
    result = []
    for p in patients:
        result.append({
            "patient_id": p.patient_id,
            "first_name": p.first_name,
            "age": p.age,
            "county": p.county,
            "epl_type": p.epl_type,
            "channel": p.channel,
            "language_pref": p.language_pref,
            "day_post_loss_today": (datetime.utcnow().date() - p.date_of_loss).days if p.date_of_loss else 0,
            "risk": "LOW",
            "active": p.active,
        })
    return {"patients": result, "total": len(result)}


@router.get("/{patient_id}", response_model=PatientOut)
def get_patient(patient_id: str, db: Session = Depends(get_db)):
    """Get a single patient's profile."""
    p = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if not p:
        raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found")
    return _to_out(p)


@router.patch("/{patient_id}/deactivate")
def deactivate_patient(patient_id: str, db: Session = Depends(get_db)):
    """
    Deactivate monitoring — called when woman completes 14-day window
    or requests withdrawal. Data is retained for surveillance.
    """
    p = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if not p:
        raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found")
    p.active = False
    db.commit()
    return {"message": f"Patient {patient_id} deactivated. Data retained.", "patient_id": patient_id}


@router.get("/stats/summary")
def patient_stats(db: Session = Depends(get_db)):
    """Dashboard stats — enrolment numbers, demographics."""
    all_p = db.query(Patient).all()
    total = len(all_p)
    if total == 0:
        return {"total": 0}

    counties = {}
    epl_types = {}
    channels  = {}
    for p in all_p:
        counties[p.county]         = counties.get(p.county, 0) + 1
        epl_types[str(p.epl_type)] = epl_types.get(str(p.epl_type), 0) + 1
        channels[str(p.channel)]   = channels.get(str(p.channel), 0) + 1

    ages = [p.age for p in all_p]
    return {
        "total_enrolled":  total,
        "active":          sum(1 for p in all_p if p.active),
        "avg_age":         round(sum(ages) / len(ages), 1),
        "youngest":        min(ages),
        "oldest":          max(ages),
        "by_county":       dict(sorted(counties.items(), key=lambda x: -x[1])),
        "by_epl_type":     epl_types,
        "by_channel":      channels,
        "consent_rate":    round(sum(1 for p in all_p if p.consent_given) / total * 100, 1),
    }


# ── Helper ────────────────────────────────────────────────────────────────────

def _to_out(p: Patient) -> PatientOut:
    today = date_cls.today()
    delta = (today - p.date_of_loss).days if p.date_of_loss else 0
    return PatientOut(
        patient_id          = p.patient_id,
        first_name          = p.first_name,
        age                 = p.age,
        county              = p.county,
        epl_type            = str(p.epl_type),
        date_of_loss        = str(p.date_of_loss),
        channel             = str(p.channel),
        language_pref       = str(p.language_pref),
        chw_id              = p.chw_id,
        enrolled_at         = str(p.enrolled_at),
        active              = p.active,
        day_post_loss_today = delta,
    )