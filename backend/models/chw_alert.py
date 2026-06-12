from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey
from core.database import Base


class CHWAlert(Base):
    __tablename__ = "chw_alerts"

    alert_id                = Column(String(10), primary_key=True)
    log_id                  = Column(String(12))
    patient_id              = Column(String(12), ForeignKey("patients.patient_id"), nullable=False)
    chw_id                  = Column(String(10), nullable=False)
    county                  = Column(String(50))
    alert_date              = Column(DateTime, default=datetime.utcnow)
    risk_level              = Column(String(12), nullable=False)
    risk_score              = Column(Integer)
    symptom_summary         = Column(Text)
    chw_notified            = Column(Boolean, default=False)
    chw_notified_at         = Column(DateTime)
    chw_response_minutes    = Column(Integer)
    home_visit_completed    = Column(Boolean, default=False)
    home_visit_completed_at = Column(DateTime)
    referral_generated      = Column(Boolean, default=False)
    referral_sent_at        = Column(DateTime)
    facility                = Column(String(100))
    outcome                 = Column(String(50))
    chw_notes               = Column(Text)
    status                  = Column(String(20), default="PENDING")