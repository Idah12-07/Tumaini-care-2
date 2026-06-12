from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Date, Text, ForeignKey
from core.database import Base


class SymptomLog(Base):
    __tablename__ = "symptom_logs"

    log_id           = Column(String(12), primary_key=True)
    patient_id       = Column(String(12), ForeignKey("patients.patient_id"), nullable=False)
    check_date       = Column(Date, nullable=False)
    day_post_loss    = Column(Integer, nullable=False)
    logged_at        = Column(DateTime, default=datetime.utcnow)
    responded        = Column(Boolean, default=False)
    message_text     = Column(Text)
    message_language = Column(String(20))
    heavy_bleeding   = Column(Boolean, default=False)
    foul_odour       = Column(Boolean, default=False)
    right_sided_pain = Column(Boolean, default=False)
    fever            = Column(Boolean, default=False)
    severe_pain      = Column(Boolean, default=False)
    dizziness        = Column(Boolean, default=False)
    vomiting         = Column(Boolean, default=False)
    no_bleeding      = Column(Boolean, default=False)
    risk_score       = Column(Integer, default=0)
    risk_level       = Column(String(12), default="UNKNOWN")
    ai_response_sent     = Column(Boolean, default=False)
    ai_response_text     = Column(Text)
    grief_mode_triggered = Column(Boolean, default=False)
    chw_alert_triggered  = Column(Boolean, default=False)
    referral_generated   = Column(Boolean, default=False)