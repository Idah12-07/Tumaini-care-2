# DHIS2 Sync Route — pull aggregate indicators, push surveillance data
"""
TUMAINI CARE — DHIS2 Sync Route
Placeholder — full integration built in Week 3.
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/status")
def dhis2_status():
    return {
        "status": "placeholder",
        "message": "DHIS2 sync will be implemented in Week 3.",
        "khis_url": "https://hiskenya.org/api"
    }
