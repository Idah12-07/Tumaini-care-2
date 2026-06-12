from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import socket

from models.patient      import Patient       # noqa
from models.symptom_log  import SymptomLog    # noqa
from models.chw_alert    import CHWAlert      # noqa
from models.conversation import Conversation  # noqa
from core.database import create_tables

logger = logging.getLogger(__name__)

from routes import companion, triage, alerts, patients, dhis2_sync, whatsapp
from routes import ussd, sms, referral

app = FastAPI(title="Tumaini Care API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://tumaini-care.vercel.app",
        "https://tumaini-care-git-main-idah.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

@app.options("/{full_path:path}")
async def preflight_handler(full_path: str):
    return {"status": "ok"}

@app.on_event("startup")
async def startup():
    try:
        create_tables()
        logger.info("✓ Tables ready")
    except Exception as e:
        logger.error(f"Startup warning: {e}")

    try:
        socket.getaddrinfo("generativelanguage.googleapis.com", 443)
        socket.getaddrinfo("api-inference.huggingface.co", 443)
        logger.info("✓ DNS warmup successful — outbound internet confirmed")
    except Exception as e:
        logger.error(f"✗ DNS warmup FAILED — {e}")
        logger.error("Outbound internet is blocked on this host")

app.include_router(companion.router,  prefix="/api/companion", tags=["AI Companion"])
app.include_router(triage.router,     prefix="/api/triage",    tags=["Symptom Triage"])
app.include_router(alerts.router,     prefix="/api/alerts",    tags=["CHW Alerts"])
app.include_router(patients.router,   prefix="/api/patients",  tags=["Patients"])
app.include_router(dhis2_sync.router, prefix="/api/dhis2",     tags=["DHIS2"])
app.include_router(ussd.router,       prefix="/api/channel",   tags=["USSD"])
app.include_router(sms.router,        prefix="/api/channel",   tags=["SMS"])
app.include_router(whatsapp.router,   prefix="/api/channel",   tags=["WhatsApp"])
app.include_router(referral.router,   prefix="/api/referral",  tags=["Referral"])

@app.get("/health")
def health():
    return {"status": "ok", "service": "tumaini-care", "version": "1.0.0"}

@app.get("/ping")
def ping():
    return "pong"

@app.get("/wake")
def wake():
    create_tables()
    return {"status": "awake", "service": "tumaini-care"}

@app.get("/")
def root():
    return {
        "service": "Tumaini Care API",
        "docs": "/docs",
        "health": "/health",
        "version": "1.0.0"
    }
