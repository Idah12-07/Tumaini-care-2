from sqlalchemy import Column, String, Boolean, DateTime, Enum as SAEnum
from sqlalchemy.sql import func
from core.database import Base
import enum

class UserRole(str, enum.Enum):
    admin   = "admin"
    chw     = "chw"
    patient = "patient"

class User(Base):
    __tablename__ = "users"

    user_id       = Column(String(50),  primary_key=True)
    phone         = Column(String(20),  unique=True, nullable=False, index=True)
    name          = Column(String(100), nullable=False)
    email         = Column(String(120), nullable=True)
    role          = Column(SAEnum(UserRole), nullable=False)
    pin_hash      = Column(String(128), nullable=False)
    county        = Column(String(50),  nullable=True)
    sub_county    = Column(String(50),  nullable=True)
    active        = Column(Boolean,     default=True)
    created_by    = Column(String(50),  nullable=True)
    created_at    = Column(DateTime,    server_default=func.now())
    last_login    = Column(DateTime,    nullable=True)

    # CHW specific
    chw_code      = Column(String(20),  nullable=True)  # official CHW ID
    facility_name = Column(String(100), nullable=True)

    # Patient specific — links portal account to patient record
    patient_id    = Column(String(50),  nullable=True)
