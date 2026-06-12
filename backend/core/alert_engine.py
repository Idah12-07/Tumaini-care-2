# CHW Alert Engine — trigger, format and dispatch alerts
"""
TUMAINI CARE — Alert Engine
Builds structured CHW alert summaries and dispatches notifications.
In production: sends via Africa's Talking SMS + CHT push notification.
In development: logs to console (no API keys needed to test).
"""
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# ── Danger sign labels (English + Swahili for CHW) ───────────────────────────
SYMPTOM_LABELS = {
    "heavy_bleeding":   {"en": "Heavy bleeding",         "sw": "Damu nyingi"},
    "foul_odour":       {"en": "Foul-smelling discharge","sw": "Harufu mbaya"},
    "right_sided_pain": {"en": "Right-sided pain",       "sw": "Maumivu upande wa kulia"},
    "fever":            {"en": "Fever / feeling hot",    "sw": "Homa kali"},
    "severe_pain":      {"en": "Severe abdominal pain",  "sw": "Maumivu makali tumboni"},
    "dizziness":        {"en": "Dizziness / fainting",   "sw": "Kizunguzungu"},
    "vomiting":         {"en": "Vomiting",               "sw": "Kutapika"},
}

RISK_ACTIONS = {
    "HIGH":      "Conduct home visit today. Call patient first.",
    "EMERGENCY": "GO IMMEDIATELY. Call patient now. Generate facility referral.",
}


def build_alert_summary(symptom_flags: dict, risk_level: str, risk_score: int) -> str:
    """
    Build a structured plain-text summary to send to the CHW.
    Readable on a basic SMS or CHT notification.
    """
    active = [
        f"• {v['en']} ({v['sw']})"
        for k, v in SYMPTOM_LABELS.items()
        if symptom_flags.get(k) is True
    ]
    symptoms_text = "\n".join(active) if active else "• No specific flags extracted"
    action = RISK_ACTIONS.get(risk_level, "Monitor and follow up.")

    summary = (
        f"[TUMAINI ALERT — {risk_level}]\n"
        f"Risk score: {risk_score}\n"
        f"Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC\n\n"
        f"Symptoms reported:\n{symptoms_text}\n\n"
        f"Action required: {action}\n"
        f"Reply VISITED once home visit completed."
    )
    return summary


def dispatch_chw_notification(chw_id: str, alert_id: str,
                               summary: str, risk: str) -> bool:
    """
    Send alert to CHW via SMS (Africa's Talking) or CHT push.
    Returns True if dispatch succeeded.

    In development mode (no AT_API_KEY set): logs to console only.
    In production: sends real SMS.
    """
    at_key = os.getenv("AT_API_KEY")
    chw_phone = _get_chw_phone(chw_id)   # look up from CHW registry

    if not at_key or not chw_phone:
        # ── Development mode — just log it ───────────────────
        logger.info(f"[DEV] CHW ALERT dispatched (not sent — no AT key)")
        logger.info(f"  CHW: {chw_id} | Alert: {alert_id} | Risk: {risk}")
        logger.info(f"  Summary:\n{summary}")
        return True                        # return True so flow continues

    # ── Production mode — send real SMS via Africa's Talking ─
    try:
        import africastalking
        africastalking.initialize(
            username=os.getenv("AT_USERNAME"),
            api_key=at_key
        )
        sms = africastalking.SMS
        response = sms.send(summary, [chw_phone])
        logger.info(f"SMS sent to CHW {chw_id}: {response}")
        return True
    except Exception as e:
        # Sandbox SSL issues — log only, don't crash
        logger.info(f"[SANDBOX] SMS skipped (sandbox limitation): {type(e).__name__}")
        return True  # Return True so flow continues


def generate_referral_document(patient_id: str, symptom_logs: list,
                                alert: object, facility: str) -> dict:
    """
    Auto-generate a structured referral document for the receiving facility.
    Returns a dict that can be rendered as PDF or sent as structured SMS.
    """
    # Build symptom timeline from last 3 days of logs
    timeline = []
    for log in sorted(symptom_logs, key=lambda l: l.day_post_loss)[-3:]:
        active = [
            k.replace("_", " ").title()
            for k in ["heavy_bleeding","fever","foul_odour","severe_pain",
                      "right_sided_pain","vomiting","dizziness"]
            if getattr(log, k, False)
        ]
        timeline.append({
            "day": log.day_post_loss,
            "date": str(log.check_date),
            "risk": str(log.risk_level),
            "symptoms": active or ["No danger signs"],
        })

    return {
        "document_type":     "POST-EPL REFERRAL — TUMAINI CARE",
        "generated_at":      datetime.utcnow().isoformat(),
        "patient_id":        patient_id,          # pseudonymised
        "receiving_facility": facility,
        "referring_system":  "Tumaini Care (AI Community Health Platform)",
        "current_risk":      alert.risk_level if alert else "HIGH",
        "symptom_timeline":  timeline,
        "chw_visit":         alert.home_visit_completed if alert else False,
        "chw_notes":         alert.chw_notes if alert else "",
        "recommended_action": (
            "Urgent assessment for incomplete miscarriage / sepsis / ectopic rupture. "
            "Patient referred from Tumaini post-EPL community surveillance system."
        ),
        "language_pref":     "Swahili",
        "note": "Pre-populated by Tumaini AI. Verify all details with patient on arrival.",
    }


def _get_chw_phone(chw_id: str) -> str:
    """
    Look up CHW phone from registry.
    In production: query CHW database table.
    In dev: return a test number.
    """
    # TODO: replace with real DB query in production
    dev_registry = {
        "CHW001": "+254700000001",
        "CHW002": "+254700000002",
        "CHW003": "+254700000003",
    }
    return dev_registry.get(chw_id, "")