"""
TUMAINI CARE — SMS Handler
Sends daily check-in SMS and receives responses via Africa's Talking.
Works on any phone, no internet required.
"""
import os
import logging
from fastapi import APIRouter, Form
from fastapi.responses import PlainTextResponse
from core.triage_engine import score_symptoms, get_risk_level
from core.alert_engine import build_alert_summary, dispatch_chw_notification
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)
router = APIRouter()

# ── Keyword maps (women reply with numbers or words) ─────────
SYMPTOM_KEYWORDS_SW = {
    "damu":     "heavy_bleeding",
    "1":        "heavy_bleeding",
    "homa":     "fever",
    "2":        "fever",
    "harufu":   "foul_odour",
    "3":        "foul_odour",
    "maumivu":  "severe_pain",
    "4":        "severe_pain",
    "upande":   "right_sided_pain",
    "5":        "right_sided_pain",
    "kizungu":  "dizziness",
    "6":        "dizziness",
    "sawa":     None,   # OK — no symptoms
    "7":        None,
    "stop":     "unsubscribe",
}

SYMPTOM_KEYWORDS_EN = {
    "bleeding": "heavy_bleeding",
    "1":        "heavy_bleeding",
    "fever":    "fever",
    "2":        "fever",
    "smell":    "foul_odour",
    "3":        "foul_odour",
    "pain":     "severe_pain",
    "4":        "severe_pain",
    "side":     "right_sided_pain",
    "5":        "right_sided_pain",
    "dizzy":    "dizziness",
    "6":        "dizziness",
    "okay":     None,
    "ok":       None,
    "fine":     None,
    "7":        None,
    "stop":     "unsubscribe",
}

DAILY_CHECKIN_SW = (
    "Habari! Mimi ni Tumaini. Je, leo una dalili zozote?\n"
    "Jibu namba:\n"
    "1=Damu nyingi 2=Homa 3=Harufu mbaya\n"
    "4=Maumivu makali 5=Maumivu upande mmoja\n"
    "6=Kizunguzungu 7=Niko sawa\n"
    "Jibu STOP kukomesha."
)

DAILY_CHECKIN_EN = (
    "Hello! I am Tumaini. Do you have any symptoms today?\n"
    "Reply with a number:\n"
    "1=Heavy bleeding 2=Fever 3=Bad smell\n"
    "4=Severe pain 5=One-sided pain\n"
    "6=Dizziness 7=I am okay\n"
    "Reply STOP to unsubscribe."
)


def send_sms(phone: str, message: str) -> bool:
    """Send SMS via Africa's Talking. Returns True if sent."""
    api_key  = os.getenv("AT_API_KEY", "")
    username = os.getenv("AT_USERNAME", "sandbox")

    if not api_key or "your_key" in api_key:
        logger.info(f"[DEV] SMS not sent (no AT key). To: {phone}")
        logger.info(f"[DEV] Message: {message[:80]}")
        return True   # Return True so flow continues in dev

    try:
        import africastalking
        africastalking.initialize(username=username, api_key=api_key)
        sms = africastalking.SMS
        response = sms.send(message, [phone])
        logger.info(f"SMS sent to {phone}: {response}")
        return True
    except Exception as e:
        logger.error(f"SMS send failed: {e}")
        return False


def send_daily_checkin(phone: str, language: str = "sw", day: int = 1) -> bool:
    """Send the daily symptom check-in SMS to a woman."""
    msg = DAILY_CHECKIN_SW if language in ("sw","Swahili") else DAILY_CHECKIN_EN
    return send_sms(phone, f"[Day {day}/14] {msg}")


def send_chw_alert_sms(chw_phone: str, summary: str) -> bool:
    """Send CHW alert via SMS."""
    return send_sms(chw_phone, summary)


@router.post("/sms/incoming")
async def sms_incoming(
    From:    str = Form(default="", alias="from"),
    To:      str = Form(default="", alias="to"),
    Text:    str = Form(default="", alias="text"),
    Date:    str = Form(default="", alias="date"),
    Id:      str = Form(default="", alias="id"),
):
    message = Text.strip()
    # basic symptom detection
    from core.triage_engine import score_symptoms, get_risk_level
    symptoms = {}
    msg_lower = message.lower()
    if any(w in msg_lower for w in ["1", "damu", "bleeding"]): symptoms["heavy_bleeding"] = True
    if any(w in msg_lower for w in ["2", "homa", "fever"]):    symptoms["fever"] = True
    if any(w in msg_lower for w in ["3", "harufu", "smell"]):  symptoms["foul_odour"] = True
    if any(w in msg_lower for w in ["4", "maumivu", "pain"]):  symptoms["severe_pain"] = True
    if any(w in msg_lower for w in ["5", "upande", "side"]):   symptoms["right_sided_pain"] = True
    if any(w in msg_lower for w in ["6", "kizungu", "dizzy"]): symptoms["dizziness"] = True

    if symptoms:
        score = score_symptoms(symptoms)
        level = get_risk_level(score)
        if level in ("HIGH", "EMERGENCY"):
            from core.alert_engine import build_alert_summary, dispatch_chw_notification
            summary = build_alert_summary(symptoms, level, score)
            dispatch_chw_notification("CHW001", f"SMS_{Id[:8]}", summary, level)
            reply = "HATARI: Nenda hospitali SASA. CHW wako amejulishwa. / URGENT: Go to hospital NOW. Your CHW has been notified."
        else:
            reply = "Asante. Tumepokea ujumbe wako. / Thank you. We received your message. Dial *384# anytime."
    else:
        reply = "Karibu Tumaini. Piga *384# kwa msaada. / Welcome to Tumaini. Dial *384# for help."

    return PlainTextResponse(content=reply)


@router.post("/sms/send-checkin")
async def trigger_checkin(phone: str, language: str = "sw", day: int = 1):
    """
    Manually trigger a check-in SMS — used for testing
    and for the scheduled daily job.
    """
    sent = send_daily_checkin(phone, language, day)
    return {"sent": sent, "phone": phone, "day": day}