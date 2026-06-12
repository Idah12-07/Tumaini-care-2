# TUMAINI CARE — AI Grief Companion Route
# Receives woman's message, calls Claude API, returns culturally-safe response
from fastapi import APIRouter
from pydantic import BaseModel
from core.claude_client import get_companion_response

router = APIRouter()

class Message(BaseModel):
    patient_id: str
    message: str
    language: str = 'swahili'  # 'swahili' | 'english'
    conversation_history: list = []

@router.post('/chat')
async def chat(msg: Message):
    response = await get_companion_response(
        patient_id=msg.patient_id,
        message=msg.message,
        language=msg.language,
        history=msg.conversation_history
    )
    return {'reply': response, 'patient_id': msg.patient_id}
