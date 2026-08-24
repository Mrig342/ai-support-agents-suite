"""Context Manager for Conversation State Management"""

import logging
from typing import Dict, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ContextManager:
    """Manages conversation context and session state."""
    
    def __init__(self, max_history: int = 50, context_window: int = 32000):
        self.max_history = max_history
        self.context_window = context_window
        self.sessions = {}
    
    def create_session(self, session_id: str, customer_id: str, 
                      request_title: str, request_body: str) -> Dict:
        """Create a new context session."""
        session = {
            "session_id": session_id,
            "customer_id": customer_id,
            "request_title": request_title,
            "conversation_history": [
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "role": "customer",
                    "message": request_body,
                    "tokens": len(request_body.split())
                }
            ],
            "session_context": {
                "active_agents": [],
                "escalation_level": 0,
                "resolution_attempts": []
            },
            "created_at": datetime.utcnow().isoformat(),
            "last_updated": datetime.utcnow().isoformat(),
            "token_usage": len(request_body.split())
        }
        
        self.sessions[session_id] = session
        logger.info(f"Session created: {session_id}")
        return session
    
    def add_message(self, session_id: str, role: str, message: str) -> Dict:
        """Add message to conversation history."""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        message_tokens = len(message.split())
        
        new_message = {
            "timestamp": datetime.utcnow().isoformat(),
            "role": role,
            "message": message,
            "tokens": message_tokens
        }
        
        session["conversation_history"].append(new_message)
        session["token_usage"] += message_tokens
        session["last_updated"] = datetime.utcnow().isoformat()
        
        logger.info(f"Message added to session {session_id}")
        return new_message
    
    def get_context_summary(self, session_id: str) -> str:
        """Generate context summary from recent messages."""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        history = session["conversation_history"]
        
        summary = f"Session {session_id}\n"
        summary += f"Customer: {session['customer_id']}\n"
        summary += f"Issue: {session['request_title']}\n\n"
        summary += "Recent Conversation:\n"
        
        for msg in history[-5:]:
            role = msg["role"].upper()
            summary += f"{role}: {msg['message'][:100]}...\n"
        
        return summary
    
    def get_full_context(self, session_id: str) -> Dict:
        """Get complete session context for escalation or handoff."""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        return session
    
    def cleanup_expired_sessions(self, timeout_hours: int = 24):
        """Remove sessions older than timeout."""
        cutoff_time = datetime.utcnow() - timedelta(hours=timeout_hours)
        expired = []
        
        for session_id, session in list(self.sessions.items()):
            last_updated = datetime.fromisoformat(session["last_updated"])
            if last_updated < cutoff_time:
                expired.append(session_id)
                del self.sessions[session_id]
        
        logger.info(f"Cleaned up {len(expired)} expired sessions")
        return len(expired)
