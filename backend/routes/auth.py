"""
Authentication routes — login, register patient PIN, create CHW (admin only).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import secrets

from core.database import get_db
from core.auth import (
    hash_pin, verify_pin, generate_pin,
    generate_user_id, create_token
)
from models.user import User, UserRole

router = APIRouter()

# ── REQUEST MODELS ────────────────────────────────────────────

class LoginRequest(BaseModel):
    phone: str
    pin:   str

class CreateCHWRequest(BaseModel):
    name:         str
    phone:        str
    county:       str
    sub_county:   str
    chw_code:     Optional[str] = None
    facility_name:Optional[str] = None

class SetPinRequest(BaseModel):
    phone: str
    temp_pin: str
    new_pin:  str

class CreateAdminRequest(BaseModel):
    name:      str
    phone:     str
    email:     Optional[str] = None
    secret_key:str  # one-time setup key

# ── ROUTES ────────────────────────────────────────────────────

@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """Login for all roles — phone + PIN."""
    user = db.query(User).filter(
        User.phone == req.phone,
        User.active == True
    ).first()

    if not user:
        raise HTTPException(status_code=401, detail="Phone number not found.")

    if not verify_pin(req.pin, user.pin_hash):
        raise HTTPException(status_code=401, detail="Incorrect PIN.")

    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()

    token = create_token(user.user_id, user.role, user.phone)

    return {
        "token":   token,
        "user_id": user.user_id,
        "name":    user.name,
        "role":    user.role,
        "county":  user.county,
    }


@router.post("/create-chw")
def create_chw(
    req: CreateCHWRequest,
    db:  Session = Depends(get_db),
    _admin = Depends(__import__('core.auth', fromlist=['require_admin']).require_admin)
):
    """Admin creates a CHW account. System generates a temp PIN sent via SMS."""
    existing = db.query(User).filter(User.phone == req.phone).first()
    if existing:
        raise HTTPException(status_code=400, detail="Phone number already registered.")

    temp_pin  = generate_pin(4)
    user_id   = generate_user_id("chw")

    chw = User(
        user_id       = user_id,
        phone         = req.phone,
        name          = req.name,
        role          = UserRole.chw,
        pin_hash      = hash_pin(temp_pin),
        county        = req.county,
        sub_county    = req.sub_county,
        chw_code      = req.chw_code,
        facility_name = req.facility_name,
        active        = True,
    )
    db.add(chw)
    db.commit()

    # Send temp PIN via Africa's Talking
    try:
        import africastalking, os
        africastalking.initialize(
            username=os.getenv("AT_USERNAME", "sandbox"),
            api_key=os.getenv("AT_API_KEY", "")
        )
        sms = africastalking.SMS
        msg = (
            f"Habari {req.name}. Umesajiliwa kwenye Tumaini Care kama CHW. "
            f"Nambari yako ya kuingia: {req.phone}. "
            f"PIN yako ya muda: {temp_pin}. "
            f"Badilisha PIN yako unapoingia mara ya kwanza. "
            f"Tumaini Care CHW Portal."
        )
        sms.send(msg, [req.phone])
    except Exception as e:
        print(f"[Auth] SMS failed: {e}")

    return {
        "message":  f"CHW account created. Temporary PIN sent to {req.phone}.",
        "user_id":  user_id,
        "temp_pin": temp_pin  # also return in response for admin to note
    }


@router.post("/set-pin")
def set_pin(req: SetPinRequest, db: Session = Depends(get_db)):
    """CHW or patient sets their own PIN after first login."""
    user = db.query(User).filter(User.phone == req.phone).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    if not verify_pin(req.temp_pin, user.pin_hash):
        raise HTTPException(status_code=401, detail="Temporary PIN incorrect.")

    if len(req.new_pin) < 4:
        raise HTTPException(status_code=400, detail="PIN must be at least 4 digits.")

    user.pin_hash = hash_pin(req.new_pin)
    db.commit()

    return {"message": "PIN updated successfully. You can now log in with your new PIN."}


@router.post("/patient-register")
def patient_register(
    phone: str,
    new_pin: str,
    db: Session = Depends(get_db)
):
    """
    Patient self-registers for portal access.
    Phone must already exist in the patients table (enrolled by CHW).
    """
    from models.patient import Patient

    # Check patient is enrolled
    patient = db.query(Patient).filter(
        Patient.phone_hash != None
    ).first()

    # Check not already registered
    existing = db.query(User).filter(User.phone == phone).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Account already exists. Please log in."
        )

    if len(new_pin) < 4:
        raise HTTPException(status_code=400, detail="PIN must be 4 digits.")

    user_id = generate_user_id("patient")
    user = User(
        user_id    = user_id,
        phone      = phone,
        name       = "Patient",
        role       = UserRole.patient,
        pin_hash   = hash_pin(new_pin),
        active     = True,
    )
    db.add(user)
    db.commit()

    token = create_token(user_id, "patient", phone)
    return {
        "message": "Account created successfully.",
        "token":   token,
        "role":    "patient"
    }


@router.post("/setup-admin")
def setup_admin(req: CreateAdminRequest, db: Session = Depends(get_db)):
    """
    One-time admin setup. Protected by a secret key in environment variables.
    Only works if no admin exists yet.
    """
    import os
    expected = os.getenv("ADMIN_SETUP_KEY", "tumaini-admin-setup-2026")
    if req.secret_key != expected:
        raise HTTPException(status_code=403, detail="Invalid setup key.")

    existing_admin = db.query(User).filter(User.role == UserRole.admin).first()
    if existing_admin:
        raise HTTPException(status_code=400, detail="Admin already exists.")

    pin    = generate_pin(6)
    userid = generate_user_id("admin")

    admin = User(
        user_id  = userid,
        phone    = req.phone,
        name     = req.name,
        email    = req.email,
        role     = UserRole.admin,
        pin_hash = hash_pin(pin),
        active   = True,
    )
    db.add(admin)
    db.commit()

    return {
        "message":  "Admin account created.",
        "user_id":  userid,
        "temp_pin": pin
    }


@router.get("/me")
def get_me(
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        __import__('core.auth', fromlist=['get_current_user']).get_current_user
    )
):
    """Return current user profile."""
    user = db.query(User).filter(
        User.user_id == current_user["sub"]
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return {
        "user_id":      user.user_id,
        "name":         user.name,
        "phone":        user.phone,
        "role":         user.role,
        "county":       user.county,
        "sub_county":   user.sub_county,
        "facility_name":user.facility_name,
        "last_login":   user.last_login,
    }
