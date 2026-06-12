from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Boolean, ForeignKey
from core.database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    conv_id              = Column(String(15), primary_key=True)
    patient_id           = Column(String(12), ForeignKey("patients.patient_id"), nullable=False)
    session_id           = Column(String(30))
    role                 = Column(String(10), nullable=False)
    content              = Column(Text, nullable=False)
    language_detected    = Column(String(20))
    day_post_loss        = Column(String(5))
    danger_sign_detected = Column(Boolean, default=False)
    escalated_to_chw     = Column(Boolean, default=False)
    model_used           = Column(String(40))
    prompt_version       = Column(String(10))
    created_at           = Column(DateTime, default=datetime.utcnow)