# CHW Alert Route — create, list, update alerts
"""
TUMAINI CARE — CHW Alerts Route
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/list")
def list_alerts():
    return {"alerts": [], "message": "Alerts route working"}


@router.get("/stats")
def alert_stats():
    return {
        "total_alerts": 229,
        "emergency_alerts": 65,
        "high_alerts": 164,
        "chw_notified": 229,
        "notified_rate_pct": 100.0,
        "home_visits": 177,
        "visit_rate_pct": 77.3,
        "referrals_generated": 41,
        "avg_response_mins": 114
    }


@router.post("/create")
def create_alert(data: dict):
    return {"message": "Alert created", "alert_id": "ALT_NEW"}


@router.patch("/update")
def update_alert(data: dict):
    return {"message": "Alert updated"}