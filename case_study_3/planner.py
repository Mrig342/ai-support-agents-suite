"""Planner Agent for Request Routing"""

import logging
from enum import Enum
from typing import List, Dict, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class AgentType(str, Enum):
    RETRIEVAL = "retrieval_agent"
    DIAGNOSTIC = "diagnostic_agent"
    INTEGRATION = "integration_agent"
    ESCALATION = "escalation_agent"

class PlannerAgent:
    """Routes support requests to appropriate specialist agents."""
    
    def __init__(self):
        self.routing_history = []
        self.agent_workload = {agent: 0 for agent in AgentType}
    
    def analyze_request(self, request_data: Dict) -> Tuple[List[AgentType], Dict]:
        """Analyze request and determine optimal agent routing."""
        agents = [AgentType.RETRIEVAL]
        
        complexity = self._assess_complexity(request_data)
        urgency = self._assess_urgency(request_data)
        category = self._categorize_request(request_data)
        requires_integration = self._check_integration_need(request_data)
        
        if complexity in ["high", "critical"]:
            agents.append(AgentType.DIAGNOSTIC)
        
        if requires_integration:
            agents.append(AgentType.INTEGRATION)
        
        if urgency in ["high", "critical"]:
            agents.append(AgentType.ESCALATION)
        
        analysis = {
            "complexity": complexity,
            "urgency": urgency,
            "category": category,
            "requires_integration": requires_integration
        }
        
        logger.info(f"Request routed to agents: {[a.value for a in agents]}")
        return agents, analysis
    
    def _assess_complexity(self, request_data: Dict) -> str:
        """Assess request complexity."""
        body = request_data.get("request_body", "").lower()
        title = request_data.get("request_title", "").lower()
        full_text = body + " " + title
        
        if any(word in full_text for word in ["crash", "system down", "data loss"]):
            return "critical"
        elif any(word in full_text for word in ["error", "failure", "integration"]):
            return "high"
        elif any(word in full_text for word in ["issue", "problem"]):
            return "medium"
        return "low"
    
    def _assess_urgency(self, request_data: Dict) -> str:
        """Assess request urgency."""
        severity = request_data.get("severity", "medium").lower()
        return "critical" if severity == "critical" else severity
    
    def _categorize_request(self, request_data: Dict) -> str:
        """Categorize the request."""
        body = request_data.get("request_body", "").lower()
        if any(word in body for word in ["login", "auth", "password"]):
            return "authentication"
        elif any(word in body for word in ["slow", "performance", "timeout"]):
            return "performance"
        elif any(word in body for word in ["sync", "data"]):
            return "data"
        return "general"
    
    def _check_integration_need(self, request_data: Dict) -> bool:
        """Check if external system integration is needed."""
        body = request_data.get("request_body", "").lower()
        return any(word in body for word in ["api", "database", "external", "integration"])
