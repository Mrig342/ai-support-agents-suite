"""Enterprise Customer Support Agent - Main Application"""

import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import logging
from datetime import datetime
from enum import Enum
import uuid

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Enterprise Support Agent")

# Enums
class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RequestStatus(str, Enum):
    RECEIVED = "received"
    ANALYZING = "analyzing"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    ESCALATED = "escalated"

# Models
class SupportRequest(BaseModel):
    customer_id: str
    request_title: str
    request_body: str
    severity: Severity
    product: str
    attachments: Optional[List[str]] = None

class SupportResponse(BaseModel):
    session_id: str
    status: RequestStatus
    assigned_agents: List[str]
    estimated_resolution_time: str
    message: str
    timestamp: str

# Mock Session Storage
SESSION_STORAGE = {}

def route_request(request: SupportRequest) -> tuple:
    """Determine which agents should handle this request."""
    agents = []
    agents.append("retrieval_agent")
    if request.severity in [Severity.HIGH, Severity.CRITICAL]:
        agents.append("diagnostic_agent")
    if "error" in request.request_body.lower() or "log" in request.request_body.lower():
        agents.append("integration_agent")
    return str(uuid.uuid4()), agents

def estimate_resolution_time(severity: Severity) -> str:
    """Estimate resolution time based on severity."""
    time_estimates = {
        Severity.LOW: "2-4 hours",
        Severity.MEDIUM: "1-2 hours",
        Severity.HIGH: "15-30 minutes",
        Severity.CRITICAL: "5-15 minutes"
    }
    return time_estimates.get(severity, "1-2 hours")

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "Enterprise Support Agent"}

@app.post("/support-request", response_model=SupportResponse)
async def submit_support_request(request: SupportRequest) -> SupportResponse:
    """Submit an enterprise support request."""
    try:
        logger.info(f"Received support request from {request.customer_id}")
        session_id, assigned_agents = route_request(request)
        est_time = estimate_resolution_time(request.severity)
        
        session_context = {
            "session_id": session_id,
            "customer_id": request.customer_id,
            "request_title": request.request_title,
            "severity": request.severity.value,
            "product": request.product,
            "conversation_history": [
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "role": "customer",
                    "message": request.request_body
                }
            ],
            "current_agents": assigned_agents,
            "escalation_ready": False,
            "created_at": datetime.utcnow().isoformat()
        }
        
        SESSION_STORAGE[session_id] = session_context
        logger.info(f"Session created: {session_id}, Agents: {assigned_agents}")
        
        return SupportResponse(
            session_id=session_id,
            status=RequestStatus.ANALYZING,
            assigned_agents=assigned_agents,
            estimated_resolution_time=est_time,
            message="Your issue is being analyzed by our support agents.",
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/session/{session_id}")
async def get_session(session_id: str):
    """Retrieve session context and conversation history."""
    if session_id not in SESSION_STORAGE:
        raise HTTPException(status_code=404, detail="Session not found")
    return SESSION_STORAGE[session_id]

@app.post("/session/{session_id}/escalate")
async def escalate_issue(session_id: str, reason: Optional[str] = None):
    """Escalate issue to human specialist."""
    if session_id not in SESSION_STORAGE:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = SESSION_STORAGE[session_id]
    session["escalation_ready"] = True
    session["escalation_reason"] = reason or "Customer requested escalation"
    session["escalated_at"] = datetime.utcnow().isoformat()
    
    logger.info(f"Issue escalated: {session_id}")
    
    return {
        "status": "escalated",
        "escalation_id": f"ESC_{session_id}",
        "message": "Your issue has been escalated to a specialist."
    }

@app.get("/sessions")
async def get_active_sessions(customer_id: Optional[str] = None):
    """Get active sessions."""
    sessions = list(SESSION_STORAGE.values())
    if customer_id:
        sessions = [s for s in sessions if s["customer_id"] == customer_id]
    return {"total_sessions": len(sessions), "sessions": sessions}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
