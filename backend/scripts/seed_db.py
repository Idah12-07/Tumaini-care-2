"""
TUMAINI CARE — Database Seeder
Loads synthetic datasets into PostgreSQL for local development and testing.

Usage:
    cd backend
    python scripts/seed_db.py

Prerequisites:
    1. PostgreSQL running (docker-compose up postgres)
    2. .env configured with DATABASE_URL
    3. Synthetic CSVs in backend/data/synthetic/
"""
import csv
import json
import sys
import os
from datetime import date, datetime
from pathlib import Path

# Add backend root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from core.database import SessionLocal, create_tables
from models.patient import Patient, EPLType, Channel, Language
from models.symptom_log import SymptomLog, RiskLevel
from models.chw_alert import CHWAlert, AlertStatus, AlertOutcome
from models.conversation import Conversation, MessageRole


DATA_DIR = Path(__file__).parent.parent / "data" / "synthetic"


def load_csv(filename: str) -> list:
    path = DATA_DIR / filename
    if not path.exists():
        print(f"  ⚠️  {filename} not found in {DATA_DIR} — skipping")
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def bool_field(val) -> bool:
    return str(val).strip().lower() == "true"


def safe_int(val, default=0) -> int:
    try:
        return int(val)
    except (ValueError, TypeError):
        return default


def safe_date(val):
    try:
        return date.fromisoformat(str(val).strip())
    except (ValueError, TypeError):
        return date.today()


# ── Seed patients ─────────────────────────────────────────────────────────────
def seed_patients(db, rows: list) -> int:
    count = 0
    for r in rows:
        if db.query(Patient).filter(Patient.patient_id == r["patient_id"]).first():
            continue

        # Map EPL type string to enum safely
        epl_raw = r.get("epl_type", "")
        epl_map = {
            "Spontaneous miscarriage (incomplete)": EPLType.spontaneous_incomplete,
            "Spontaneous miscarriage (complete)":   EPLType.spontaneous_complete,
            "Missed miscarriage":                   EPLType.missed,
            "Ectopic pregnancy":                    EPLType.ectopic,
            "Chemical pregnancy":                   EPLType.chemical,
            "Molar pregnancy":                      EPLType.molar,
        }
        epl = epl_map.get(epl_raw, EPLType.spontaneous_incomplete)

        channel_map = {"WhatsApp": Channel.whatsapp, "SMS": Channel.sms, "USSD": Channel.ussd}
        lang_map    = {"Swahili": Language.swahili, "English": Language.english, "Swahili+dialect": Language.mixed}

        p = Patient(
            patient_id            = r["patient_id"],
            phone_hash            = r.get("phone_hash", f"hash_{r['patient_id']}"),
            first_name            = r.get("first_name", "Unknown"),
            last_name_init        = r.get("last_name", "X")[0].upper(),
            age                   = safe_int(r.get("age"), 25),
            county                = r.get("county", "Nairobi"),
            sub_county            = r.get("sub_county"),
            rural                 = bool_field(r.get("rural", "True")),
            epl_type              = epl,
            gestational_age_weeks = safe_int(r.get("gestational_age_weeks")),
            date_of_loss          = safe_date(r.get("date_of_loss")),
            parity                = safe_int(r.get("parity")),
            prior_losses          = safe_int(r.get("prior_losses")),
            facility_of_diagnosis = r.get("facility_of_diagnosis"),
            channel               = channel_map.get(r.get("channel", "WhatsApp"), Channel.whatsapp),
            language_pref         = lang_map.get(r.get("language_pref", "Swahili"), Language.swahili),
            chw_id                = r.get("chw_id"),
            enrolled              = bool_field(r.get("enrolled", "True")),
            consent_given         = bool_field(r.get("consent_given", "True")),
            enrolled_at           = datetime.utcnow(),
            active                = True,
        )
        db.add(p)
        count += 1
    db.commit()
    return count


# ── Seed symptom logs ─────────────────────────────────────────────────────────
def seed_symptom_logs(db, rows: list) -> int:
    count = 0
    for r in rows:
        if db.query(SymptomLog).filter(SymptomLog.log_id == r["log_id"]).first():
            continue

        risk_map = {
            "LOW": RiskLevel.low, "MODERATE": RiskLevel.moderate,
            "HIGH": RiskLevel.high, "EMERGENCY": RiskLevel.emergency,
        }
        risk = risk_map.get(r.get("risk_level", "UNKNOWN"), RiskLevel.unknown)

        log = SymptomLog(
            log_id           = r["log_id"],
            patient_id       = r["patient_id"],
            check_date       = safe_date(r.get("check_date")),
            day_post_loss    = safe_int(r.get("day_post_loss"), 1),
            responded        = bool_field(r.get("responded")),
            message_text     = r.get("message_text", ""),
            heavy_bleeding   = bool_field(r.get("heavy_bleeding")),
            fever            = bool_field(r.get("fever")),
            foul_odour       = bool_field(r.get("foul_odour")),
            severe_pain      = bool_field(r.get("severe_pain")),
            right_sided_pain = bool_field(r.get("right_sided_pain")),
            vomiting         = bool_field(r.get("vomiting")),
            risk_level       = risk,
            ai_response_sent    = bool_field(r.get("ai_response_sent")),
            grief_mode_triggered = bool_field(r.get("grief_mode_triggered")),
        )
        db.add(log)
        count += 1

    db.commit()
    return count


# ── Seed CHW alerts ───────────────────────────────────────────────────────────
def seed_chw_alerts(db, rows: list) -> int:
    count = 0
    for r in rows:
        if db.query(CHWAlert).filter(CHWAlert.alert_id == r["alert_id"]).first():
            continue

        outcome_map = {
            "Stabilised at home":         AlertOutcome.stabilised,
            "Admitted":                   AlertOutcome.admitted,
            "Treated and discharged":     AlertOutcome.discharged,
            "Ongoing monitoring":         AlertOutcome.monitoring,
            "No visit":                   AlertOutcome.no_visit,
        }

        alert = CHWAlert(
            alert_id              = r["alert_id"],
            log_id                = r.get("log_id"),
            patient_id            = r["patient_id"],
            chw_id                = r.get("chw_id", "CHW001"),
            county                = r.get("county", ""),
            alert_date            = datetime.utcnow(),
            risk_level            = r.get("risk_level", "HIGH"),
            chw_notified          = bool_field(r.get("chw_notified", "True")),
            chw_response_minutes  = safe_int(r.get("chw_response_minutes")),
            home_visit_completed  = bool_field(r.get("home_visit_completed")),
            referral_generated    = bool_field(r.get("referral_generated")),
            facility              = r.get("facility", ""),
            outcome               = outcome_map.get(r.get("outcome", ""), AlertOutcome.monitoring),
            status                = AlertStatus.completed,
        )
        db.add(alert)
        count += 1

    db.commit()
    return count


# ── Seed grief conversations ──────────────────────────────────────────────────
def seed_conversations(db) -> int:
    path = DATA_DIR / "grief_conversations.json"
    if not path.exists():
        print(f"  ⚠️  grief_conversations.json not found — skipping")
        return 0

    with open(path, encoding="utf-8") as f:
        convos = json.load(f)

    count = 0
    for i, turn in enumerate(convos):
        conv_id = f"CONV{str(i+1).zfill(5)}"
        if db.query(Conversation).filter(Conversation.conv_id == conv_id).first():
            continue

        role_map = {"user": MessageRole.user, "tumaini": MessageRole.assistant}
        c = Conversation(
            conv_id           = conv_id,
            patient_id        = "TUM0001",           # assign to first patient
            session_id        = "SEED_SESSION_001",
            role              = role_map.get(turn.get("turn"), MessageRole.user),
            content           = turn.get("text", ""),
            language_detected = turn.get("lang", "swahili"),
            model_used        = "claude-sonnet-4-20250514",
            prompt_version    = "v1.0",
            created_at        = datetime.utcnow(),
        )
        db.add(c)
        count += 1

    db.commit()
    return count


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n🌱 TUMAINI CARE — Database Seeder")
    print("=" * 45)

    print("\n📦 Creating tables...")
    create_tables()
    print("  ✅ Tables ready")

    db = SessionLocal()

    print("\n📂 Loading synthetic data from:", DATA_DIR)

    patients_rows = load_csv("patients.csv")
    log_rows      = load_csv("symptom_logs.csv")
    alert_rows    = load_csv("chw_alerts.csv")

    print(f"\n👩 Seeding patients ({len(patients_rows)} rows)...")
    n = seed_patients(db, patients_rows)
    print(f"  ✅ {n} patients inserted")

    print(f"\n📋 Seeding symptom logs ({len(log_rows)} rows)...")
    n = seed_symptom_logs(db, log_rows)
    print(f"  ✅ {n} symptom logs inserted")

    print(f"\n🚨 Seeding CHW alerts ({len(alert_rows)} rows)...")
    n = seed_chw_alerts(db, alert_rows)
    print(f"  ✅ {n} alerts inserted")

    print(f"\n💬 Seeding grief conversations...")
    n = seed_conversations(db)
    print(f"  ✅ {n} conversation turns inserted")

    db.close()

    print("\n" + "=" * 45)
    print("✅ Database seeded successfully!")
    print("\nNow run:")
    print("  uvicorn backend.main:app --reload")
    print("  Then open: http://127.0.0.1:8000/docs")
    print("=" * 45 + "\n")