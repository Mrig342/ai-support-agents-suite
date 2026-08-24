"""E-Commerce Customer Support Agent - Main Application"""

import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging
from datetime import datetime

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="E-Commerce Support Agent")

# Models
class CustomerQuery(BaseModel):
    user_id: str
    message: str
    session_id: str
    order_id: Optional[str] = None

class AgentResponse(BaseModel):
    response: str
    intent: str
    requires_escalation: bool
    order_id: Optional[str] = None
    confidence: float
    timestamp: str

# Mock Knowledge Base
KNOWLEDGE_BASE = {
    "order_tracking": {
        "intent_keywords": ["where", "order", "track", "delivery", "when", "arrive"],
        "template": "Your order {order_id} is currently {status}. Expected delivery: {expected_date}."
    },
    "return_request": {
        "intent_keywords": ["return", "refund", "exchange", "wrong item"],
        "template": "I can help you process a return. Please provide your order ID to begin."
    },
    "payment_issue": {
        "intent_keywords": ["payment", "charged", "billing", "credit card"],
        "template": "I'll help you resolve your payment issue. Let me verify your account details."
    },
    "product_question": {
        "intent_keywords": ["size", "color", "specifications", "material", "available"],
        "template": "Let me find the product information for you."
    }
}

# Mock Order Database
ORDER_DATABASE = {
    "ORDER_12345": {
        "status": "in_transit",
        "expected_delivery": "2024-08-26",
        "items": ["Widget A", "Widget B"],
        "customer_id": "customer_123"
    },
    "ORDER_67890": {
        "status": "delivered",
        "delivery_date": "2024-08-20",
        "items": ["Gadget X"],
        "customer_id": "customer_456"
    }
}

def identify_intent(message: str) -> tuple[str, float]:
    """Identify customer intent from message."""
    message_lower = message.lower()
    
    for intent, config in KNOWLEDGE_BASE.items():
        for keyword in config["intent_keywords"]:
            if keyword in message_lower:
                return intent, 0.85
    
    return "general_inquiry", 0.5

def retrieve_order_info(order_id: str) -> Optional[dict]:
    """Retrieve order information from database."""
    return ORDER_DATABASE.get(order_id)

def generate_response(intent: str, order_id: Optional[str], message: str) -> str:
    """Generate response based on intent and retrieved information."""
    
    if intent == "order_tracking" and order_id:
        order_info = retrieve_order_info(order_id)
        if order_info:
            return (
                f"Your order {order_id} is currently {order_info['status']}. "
                f"Expected delivery: {order_info['expected_delivery']}. "
                f"Would you like delivery updates?"
            )
    
    if intent == "return_request":
        return "I can help you initiate a return. Please share your order ID to proceed."
    
    if intent == "payment_issue":
        return "I'll help you resolve your payment issue. Let me verify your account details."
    
    if intent == "product_question":
        return "Let me find the product information for you."
    
    return "Thank you for your query. How can I assist you further?"

def requires_human_escalation(intent: str, message: str) -> bool:
    """Determine if query requires human escalation."""
    complex_keywords = [
        "complaint", "issue", "problem", "urgent", "help",
        "confused", "not working", "broken", "damaged"
    ]
    message_lower = message.lower()
    
    # Escalate complex issues
    if any(keyword in message_lower for keyword in complex_keywords):
        return True
    
    # Escalate payment-related issues
    if intent == "payment_issue":
        return True
    
    return False

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "E-Commerce Support Agent"}

@app.post("/chat", response_model=AgentResponse)
async def chat(query: CustomerQuery) -> AgentResponse:
    """Process customer query and generate response."""
    
    try:
        logger.info(f"Processing query from {query.user_id}: {query.message}")
        
        # Identify intent
        intent, confidence = identify_intent(query.message)
        
        # Generate response
        response_text = generate_response(intent, query.order_id, query.message)
        
        # Check if escalation is needed
        escalation_needed = requires_human_escalation(intent, query.message)
        
        # Log the interaction
        logger.info(f"Intent: {intent}, Escalation: {escalation_needed}")
        
        return AgentResponse(
            response=response_text,
            intent=intent,
            requires_escalation=escalation_needed,
            order_id=query.order_id,
            confidence=confidence,
            timestamp=datetime.utcnow().isoformat()
        )
    
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/orders/{order_id}")
async def get_order(order_id: str):
    """Retrieve order information."""
    order = retrieve_order_info(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.post("/orders/{order_id}/return")
async def initiate_return(order_id: str, reason: str):
    """Initiate a return request."""
    order = retrieve_order_info(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return {
        "status": "return_initiated",
        "order_id": order_id,
        "reason": reason,
        "return_id": f"RET_{order_id}_{datetime.utcnow().timestamp()}",
        "message": "Return request initiated. You will receive a return label via email."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
