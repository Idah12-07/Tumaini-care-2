from fastapi import APIRouter, Form
from fastapi.responses import PlainTextResponse
from core.claude_client import get_companion_response
from core.alert_engine import build_alert_summary, dispatch_chw_notification
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

DANGER_WORDS = [
    "damu nyingi","heavy bleeding","harufu mbaya","foul smell",
    "maumivu makali","severe pain","upande wa kulia","right side",
    "homa kali","high fever","kizunguzungu","fainting","dizzy",
    "ninaogopa","i am scared","help","msaada"
]

def detect_danger(text: str) -> dict:
    """Detect danger signs from free text without exposing content."""
    text_lower = text.lower()
    symptoms = {}
    if any(w in text_lower for w in ["damu nyingi","heavy bleeding","bleeding"]):
        symptoms["heavy_bleeding"] = True
    if any(w in text_lower for w in ["homa","fever","joto kali"]):
        symptoms["fever"] = True
    if any(w in text_lower for w in ["harufu","smell","foul"]):
        symptoms["foul_odour"] = True
    if any(w in text_lower for w in ["upande wa kulia","right side","right pain"]):
        symptoms["right_sided_pain"] = True
    if any(w in text_lower for w in ["maumivu makali","severe pain","sharp pain"]):
        symptoms["severe_pain"] = True
    if any(w in text_lower for w in ["kizunguzungu","dizzy","faint"]):
        symptoms["dizziness"] = True
    return symptoms


@router.post("/whatsapp/incoming")
async def whatsapp_incoming(
    Body: str = Form(default=""),
    From: str = Form(default=""),
):
    message = Body.strip()
    phone   = From.replace("whatsapp:", "").strip()

    # 1. Detect danger signs silently
    symptoms = detect_danger(message)
    
    if symptoms:
        from core.triage_engine import score_symptoms, get_risk_level
        score = score_symptoms(symptoms)
        level = get_risk_level(score)
        
        if level in ("HIGH", "EMERGENCY"):
            # CHW gets clinical summary ONLY — never the conversation text
            summary = (
                f"[TUMAINI WhatsApp ALERT — {level}]\n"
                f"Phone: {phone[-4:]}xxxx\n"
                f"Danger signs detected: {', '.join(symptoms.keys())}\n"
                f"Risk score: {score}\n"
                f"Action: Contact patient immediately.\n"
                f"Note: Conversation content is confidential."
            )
            dispatch_chw_notification("CHW001", f"WA_{phone[-6:]}", summary, level)
            logger.warning(f"WhatsApp CHW alert triggered | {level} | {phone[-4:]}xxxx")

    # 2. Get AI companion response (confidential — never logged to CHW)
    reply = await get_companion_response(
        patient_id="WA_USER",
        message=message,
        language="swahili",
        history=[]
    )

    # 3. Return TwiML to Twilio
    # Escape XML special characters
    safe_reply = reply.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{safe_reply}</Message>
</Response>"""
    return PlainTextResponse(content=twiml, media_type="text/xml")