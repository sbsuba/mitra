"""
Mitra FastAPI Ambient Service
Accepts check-in trigger messages and feeds into ADK workflow.
Runs on port 8080. Use for local testing and cloud deployment.
"""
import logging
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
from app.agent import (
    sanitise_input,
    calculate_risk_score,
    get_risk_level,
    should_escalate_crisis,
    get_selfcare_recommendations,
    get_crisis_resources
)
from app.config import DISCLAIMER

# Standard Python logging — no cloud telemetry locally
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Mitra",
    description="The friend who notices — before you do.",
    version="1.0.0"
)

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "local")
AGENT_RUNTIME_ID = os.getenv("AGENT_RUNTIME_ID", "local")


class CheckInRequest(BaseModel):
    """Daily check-in request payload."""
    user_id: str
    signals: dict
    language: Optional[str] = "en"
    country: Optional[str] = "US"


class CheckInResponse(BaseModel):
    """Daily check-in response payload."""
    user_id: str
    risk_score: int
    risk_level: str
    message: str
    recommendations: Optional[list] = None
    crisis_resources: Optional[dict] = None
    disclaimer: str
    security_event: Optional[bool] = False


@app.get("/", response_class=HTMLResponse)
async def root():
    """Mitra health check and welcome page."""
    return """
    <html>
    <head><title>Mitra</title></head>
    <body style="background:#0f0f1a;color:#e0e0ff;
                 font-family:sans-serif;padding:2rem;">
        <h1>Mitra</h1>
        <p>The friend who notices — before you do.</p>
        <p>Status: Running</p>
        <p><a href="/docs" style="color:#7c7cff">API Docs</a></p>
    </body>
    </html>
    """


@app.post("/checkin", response_model=CheckInResponse)
async def checkin(request: CheckInRequest):
    """
    Process a daily check-in and return risk assessment.

    Args:
        request: CheckInRequest with user_id, signals, language, country.

    Returns:
        CheckInResponse with risk score, level, and recommendations.
    """
    logger.info(f"Check-in received for user: {request.user_id}")

    # Step 1: Security screen
    cleaned = sanitise_input(request.signals)
    if cleaned.get("security_event"):
        logger.warning(f"Security event for user: {request.user_id}")
        return CheckInResponse(
            user_id=request.user_id,
            risk_score=0,
            risk_level="security_event",
            message="Your input contained unexpected content. "
                    "A human will review your check-in.",
            disclaimer=DISCLAIMER,
            security_event=True
        )

    # Step 2: Calculate risk score
    try:
        score = calculate_risk_score(cleaned)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    level = get_risk_level(score)
    logger.info(f"Risk score: {score}, level: {level}")

    # Step 3: Route based on risk level
    if level == "low":
        recs = get_selfcare_recommendations(cleaned)
        return CheckInResponse(
            user_id=request.user_id,
            risk_score=score,
            risk_level=level,
            message=(
                f"Your signal today looks healthy "
                f"(score: {score}/100). "
                f"Here are some ways to stay that way:"
            ),
            recommendations=recs,
            disclaimer=DISCLAIMER
        )

    elif level == "watch":
        recs = get_selfcare_recommendations(cleaned)
        return CheckInResponse(
            user_id=request.user_id,
            risk_score=score,
            risk_level=level,
            message=(
                f"Some early signals detected (score: {score}/100). "
                f"These patterns are worth paying attention to. "
                f"Here is one small thing you can do today:"
            ),
            recommendations=recs,
            disclaimer=DISCLAIMER
        )

    else:
        # High risk — return crisis resources
        resources = get_crisis_resources(
            request.country,
            request.language
        )
        return CheckInResponse(
            user_id=request.user_id,
            risk_score=score,
            risk_level=level,
            message=(
                f"Mitra has noticed some patterns "
                f"(score: {score}/100) that suggest "
                f"you might benefit from speaking with someone. "
                f"Here are some resources that can help:"
            ),
            crisis_resources=resources,
            disclaimer=DISCLAIMER
        )


@app.get("/health")
async def health():
    """Health check endpoint for deployment monitoring."""
    return {"status": "healthy", "service": "mitra", "version": "1.0.0"}


@app.post("/trigger/checkin")
async def trigger_checkin(payload: dict):
    """
    Ambient trigger endpoint for Pub/Sub integration.
    Accepts Pub/Sub push messages and processes check-ins.

    Args:
        payload: Pub/Sub message payload with check-in data.

    Returns:
        Processing result.
    """
    data = payload.get("data", {})
    if isinstance(data, str):
        import base64
        import json
        data = json.loads(base64.b64decode(data).decode())

    logger.info(f"Ambient trigger received: {data}")
    return {"status": "received", "data": data}
