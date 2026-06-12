import hashlib
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, Date, DateTime
from core.database import Base


class Patient(Base):
    __tablename__ = "patients"

    patient_id            = Column(String(12), primary_key=True)
    phone_hash            = Column(String(64), unique=True, nullable=False)
    first_name            = Column(String(50), nullable=False)
    last_name_init        = Column(String(5),  nullable=False)
    age                   = Column(Integer, nullable=False)
    county                = Column(String(50), nullable=False)
    sub_county            = Column(String(80))
    rural                 = Column(Boolean, default=True)
    epl_type              = Column(String(60))
    gestational_age_weeks = Column(Integer)
    date_of_loss          = Column(Date, nullable=False)
    parity                = Column(Integer, default=0)
    prior_losses          = Column(Integer, default=0)
    facility_of_diagnosis = Column(String(100))
    channel               = Column(String(20), default="WhatsApp")
    language_pref         = Column(String(30), default="Swahili")
    chw_id                = Column(String(10))
    enrolled_by           = Column(String(50))
    enrolled              = Column(Boolean, default=True)
    consent_given         = Column(Boolean, default=False)
    enrolled_at           = Column(DateTime, default=datetime.utcnow)
    active                = Column(Boolean, default=True)

    @staticmethod
    def hash_phone(phone: str) -> str:
        return hashlib.sha256(phone.strip().encode()).hexdigest()