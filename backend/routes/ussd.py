"""
TUMAINI CARE — USSD Flow Handler
Handles Africa's Talking USSD callbacks.
Women dial *384*SHORTCODE# and navigate a menu to report symptoms.
Zero cost to the woman. Works on any phone with a SIM.

Flow:
  Level 1: Main menu (language)
  Level 2: Daily check-in symptoms
  Level 3: Severity / confirmation
  Level 4: Grief support option
"""
from fastapi import APIRouter, Form
from fastapi.responses import PlainTextResponse
from core.triage_engine import score_symptoms, get_risk_level
from core.alert_engine import build_alert_summary, dispatch_chw_notification
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

sessions = {}


# Replace this:
# sessions = {}
#
# With this — stores session data in the USSD text itself, no memory needed:

def parse_session(text: str) -> dict:
    """Parse session state from USSD text string."""
    parts = [p for p in text.split("*") if p]
    return {"parts": parts, "step": len(parts)}


@router.post("/ussd", response_class=PlainTextResponse)
async def ussd_callback(
    sessionId:   str = Form(...),
    phoneNumber: str = Form(...),
    networkCode: str = Form(...),
    serviceCode: str = Form(...),
    text:        str = Form(default="")
):
    """
    Africa's Talking calls this endpoint every time a woman
    presses a key on the USSD menu. We read `text` to know
    what she has entered so far (e.g. "1*2*3").
    """
    parts = [p for p in text.split("*") if p]
    step  = len(parts)

    phone = phoneNumber.strip()
    logger.info(f"USSD | session={sessionId} | phone={phone} | text={text!r} | step={step}")

    # ── Step 0 — Welcome / language selection ─────────────────
    if step == 0:
        sessions[sessionId] = {"phone": phone, "symptoms": {}, "language": "sw"}
        return (
            "CON Karibu Tumaini / Welcome to Tumaini\n"
            "Chagua lugha / Choose language:\n"
            "1. Kiswahili\n"
            "2. English"
        )

    # ── Step 1 — Language chosen, show symptom menu ───────────
    if step == 1:
        lang = "sw" if parts[0] == "1" else "en"
        sessions[sessionId] = {"phone": phone, "symptoms": {}, "language": lang}

        if lang == "sw":
            return (
                "CON Je, una dalili hizi leo?\n"
                "1. Damu nyingi (kutoka sana)\n"
                "2. Homa / joto kali\n"
                "3. Harufu mbaya\n"
                "4. Maumivu makali tumboni\n"
                "5. Maumivu upande mmoja tu\n"
                "6. Kizunguzungu / udhaifu\n"
                "7. Hakuna dalili - niko sawa\n"
                "8. Nahitaji msaada wa kihisia"
            )
        else:
            return (
                "CON Do you have any of these symptoms today?\n"
                "1. Heavy bleeding (soaking)\n"
                "2. Fever / feeling very hot\n"
                "3. Foul-smelling discharge\n"
                "4. Severe abdominal pain\n"
                "5. One-sided pain only\n"
                "6. Dizziness / weakness\n"
                "7. No symptoms - I am okay\n"
                "8. I need emotional support"
            )

    # ── Step 2 — Symptom selected, process and respond ────────
    if step == 2:
        session  = sessions.get(sessionId, {"symptoms": {}, "language": "en"})
        lang     = session.get("language", "en")
        choice   = parts[1]
        symptoms = {}

        SYMPTOM_MAP = {
            "1": "heavy_bleeding",
            "2": "fever",
            "3": "foul_odour",
            "4": "severe_pain",
            "5": "right_sided_pain",
            "6": "dizziness",
        }

        # Grief support request
        if choice == "8":
            if lang == "sw":
                return (
                    "END Tunakusikia. Kupoteza mimba ni jambo gumu sana.\n"
                    "Wewe si peke yako. Piga simu CHW wako au nenda hospitali\n"
                    "kwa msaada zaidi. Tumaini iko nawe."
                )
            else:
                return (
                    "END We hear you. Pregnancy loss is very hard.\n"
                    "You are not alone. Please call your CHW or visit\n"
                    "a health facility for more support. Tumaini is with you."
                )

        # No symptoms — reassure
        if choice == "7":
            if lang == "sw":
                return (
                    "END Asante kwa kuripoti. Furaha kusikia uko sawa.\n"
                    "Tutakupigia ujumbe kesho. Endelea kupumzika vizuri."
                )
            else:
                return (
                    "END Thank you for checking in. Glad you are doing okay.\n"
                    "We will message you again tomorrow. Rest well."
                )

        # Map choice to symptom
        sym_key = SYMPTOM_MAP.get(choice)
        if sym_key:
            symptoms[sym_key] = True

        # Score the symptom
        score = score_symptoms(symptoms)
        level = get_risk_level(score)
        sessions[sessionId]["symptoms"] = symptoms

        # Trigger CHW alert if HIGH or EMERGENCY
        if level in ("HIGH", "EMERGENCY"):
            summary = build_alert_summary(symptoms, level, score)
            dispatch_chw_notification(
                chw_id="CHW001",  # In production: look up from patient record
                alert_id=f"USSD_{sessionId[:8]}",
                summary=summary,
                risk=level
            )
            logger.warning(f"USSD ALERT triggered | {phone} | {level} | score={score}")

            if lang == "sw":
                return (
                    f"END ⚠️ HATARI: Dalili zako zinahitaji msaada wa haraka.\n"
                    f"Tafadhali nenda hospitali SASA HIVI au mpigie simu mtu.\n"
                    f"CHW wako amepokea taarifa na atakuja hivi karibuni.\n"
                    f"Kiwango: {level}"
                )
            else:
                return (
                    f"END ⚠️ URGENT: Your symptoms need immediate attention.\n"
                    f"Please go to a health facility NOW or call someone.\n"
                    f"Your CHW has been notified and will visit you soon.\n"
                    f"Risk level: {level}"
                )

        elif level == "MODERATE":
            if lang == "sw":
                return (
                    "END Asante. Dalili zako zinahitaji ufuatiliaji.\n"
                    "CHW wako atakupigia simu leo. Kama hali inazidi,\n"
                    "nenda hospitali haraka. Jibu hii: STOP kukomesha ujumbe."
                )
            else:
                return (
                    "END Thank you. Your symptoms need monitoring.\n"
                    "Your CHW will call you today. If symptoms worsen,\n"
                    "go to a health facility immediately."
                )
        else:
            if lang == "sw":
                return (
                    "END Asante kwa kuripoti leo. Uko salama.\n"
                    "Tutakupigia ujumbe kesho asubuhi.\n"
                    "Piga *384*4993# wakati wowote ukihisi vibaya."
                )
            else:
                return (
                    "END Thank you for checking in today. You are safe.\n"
                    "We will message you again tomorrow morning.\n"
                    "Dial *384*4993# anytime you feel unwell."
                )

    # Fallback
    return "END Samahani, jaribu tena. / Sorry, please try again. Dial *384*4993#"