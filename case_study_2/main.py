"""Banking Customer Support Agent - Main Application"""

import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import logging
from datetime import datetime
from enum import Enum

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Banking Support Agent")

# Enums
class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Intent(str, Enum):
    TRANSACTION_INQUIRY = "transaction_inquiry"
    CARD_BLOCKED = "card_blocked"
    ACCOUNT_LOCKED = "account_locked"
    BALANCE_INQUIRY = "balance_inquiry"
    TRANSFER_HELP = "transfer_help"
    FRAUD_ALERT = "fraud_alert"
    BILLING_ISSUE = "billing_issue"
    GENERAL_INQUIRY = "general_inquiry"

# Models
class SecureChat(BaseModel):
    customer_id: str
    message: str
    session_token: str
    encrypted: bool = True

class IdentityVerification(BaseModel):
    customer_id: str
    verification_method: str  # "security_questions", "otp", "biometric"
    verification_data: dict

class BankingResponse(BaseModel):
    response: str
    intent: Intent
    risk_level: RiskLevel
    requires_escalation: bool
    compliance_check: str
    timestamp: str
    session_id: str

# Mock Customer Database with Security Info
CUSTOMER_DATABASE = {
    "CUST_123456": {
        "name": "John Doe",
        "accounts": ["ACC_111111", "ACC_222222"],
        "cards": ["CARD_XYZ789"],
        "status": "active",
        "mfa_enabled": True,
        "verified": True
    },
    "CUST_789012": {
        "name": "Jane Smith",
        "accounts": ["ACC_333333"],
        "cards": ["CARD_ABC123"],
        "status": "active",
        "mfa_enabled": True,
        "verified": False
    }
}

# Mock Account Database
ACCOUNT_DATABASE = {
    "ACC_111111": {
        "account_type": "checking",
        "balance": 5000.00,
        "status": "active",
        "last_transaction": "2024-08-24T10:30:00Z"
    },
    "ACC_222222": {
        "account_type": "savings",
        "balance": 25000.00,
        "status": "active",
        "last_transaction": "2024-08-20T15:45:00Z"
    },
    "ACC_333333": {
        "account_type": "checking",
        "balance": 8500.00,
        "status": "frozen",
        "last_transaction": "2024-08-19T09:15:00Z"
    }
}

# Mock Transactions
TRANSACTIONS = {
    "ACC_111111": [
        {
            "id": "TXN_001",
            "amount": 500.00,
            "type": "debit",
            "status": "pending",
            "description": "Online Purchase",
            "timestamp": "2024-08-24T10:30:00Z"
        },
        {
            "id": "TXN_002",
            "amount": 2000.00,
            "type": "credit",
            "status": "completed",
            "description": "Direct Deposit",
            "timestamp": "2024-08-22T08:00:00Z"
        }
    ]
}

def identify_intent(message: str) -> tuple[Intent, float]:
    """Identify banking intent from message."""
    message_lower = message.lower()
    
    intent_keywords = {
        Intent.TRANSACTION_INQUIRY: ["transaction", "pending", "why", "status"],
        Intent.CARD_BLOCKED: ["card", "blocked", "declined", "declined"],
        Intent.ACCOUNT_LOCKED: ["locked", "frozen", "access"],
        Intent.BALANCE_INQUIRY: ["balance", "how much", "available"],
        Intent.TRANSFER_HELP: ["transfer", "send", "wire"],
        Intent.FRAUD_ALERT: ["fraud", "unauthorized", "suspicious"],
        Intent.BILLING_ISSUE: ["bill", "charge", "fee"],
    }
    
    for intent, keywords in intent_keywords.items():
        if any(keyword in message_lower for keyword in keywords):
            return intent, 0.85
    
    return Intent.GENERAL_INQUIRY, 0.5

def assess_risk_level(intent: Intent, customer_id: str) -> RiskLevel:
    """Assess risk level based on intent and customer profile."""
    
    if intent in [Intent.FRAUD_ALERT, Intent.CARD_BLOCKED, Intent.ACCOUNT_LOCKED]:
        return RiskLevel.HIGH
    
    customer = CUSTOMER_DATABASE.get(customer_id)
    if customer and not customer.get("verified"):
        return RiskLevel.MEDIUM
    
    if intent == Intent.TRANSFER_HELP:
        return RiskLevel.MEDIUM
    
    return RiskLevel.LOW

def compliance_check(customer_id: str, message: str, risk_level: RiskLevel) -> str:
    """Perform compliance validation."""
    
    customer = CUSTOMER_DATABASE.get(customer_id)
    
    # Check if customer exists and is verified
    if not customer:
        return "failed: customer_not_found"
    
    # High-risk operations require additional verification
    if risk_level == RiskLevel.HIGH:
        if not customer.get("verified"):
            return "conditional: identity_verification_required"
    
    # Check for sensitive keywords
    sensitive_keywords = ["password", "ssn", "pin", "credit card number"]
    if any(keyword in message.lower() for keyword in sensitive_keywords):
        return "conditional: pii_handling_required"
    
    return "passed"

def generate_response(intent: Intent, customer_id: str, message: str, risk_level: RiskLevel) -> str:
    """Generate appropriate response based on intent and risk level."""
    
    customer = CUSTOMER_DATABASE.get(customer_id)
    
    if intent == Intent.TRANSACTION_INQUIRY:
        if "pending" in message.lower():
            return "Pending transactions are temporary holds by merchants and usually complete within a few business days."
        return "Transactions are processed securely. Let me check your account details for you."
    
    if intent == Intent.CARD_BLOCKED:
        return "For security reasons, I need to verify your identity before helping you unblock the card or escalating this request."
    
    if intent == Intent.ACCOUNT_LOCKED:
        return "Your account appears to be locked. This is a security measure. Please verify your identity to unlock it."
    
    if intent == Intent.BALANCE_INQUIRY:
        if customer:
            accounts = customer.get("accounts", [])
            if accounts:
                account = ACCOUNT_DATABASE.get(accounts[0])
                if account:
                    return f"Your current balance is ${account['balance']:.2f}. Would you like to see more details?"
        return "I can help you check your balance. Please confirm your account."
    
    if intent == Intent.FRAUD_ALERT:
        return "I'm concerned about potential fraud on your account. Let me transfer you to our fraud investigation team immediately."
    
    return "Thank you for contacting us. How can I help you today?"

def requires_escalation(risk_level: RiskLevel, intent: Intent) -> bool:
    """Determine if escalation to human agent is required."""
    
    if risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
        if intent in [Intent.FRAUD_ALERT, Intent.CARD_BLOCKED, Intent.ACCOUNT_LOCKED]:
            return True
    
    return False

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "Banking Support Agent"}

@app.post("/secure-chat", response_model=BankingResponse)
async def secure_chat(chat: SecureChat) -> BankingResponse:
    """Process secure banking query with compliance checks."""
    
    try:
        logger.info(f"Processing secure query from {chat.customer_id}")
        
        # Identify intent
        intent, confidence = identify_intent(chat.message)
        
        # Assess risk
        risk_level = assess_risk_level(intent, chat.customer_id)
        
        # Perform compliance check
        compliance_result = compliance_check(chat.customer_id, chat.message, risk_level)
        
        # Generate response
        response_text = generate_response(intent, chat.customer_id, chat.message, risk_level)
        
        # Determine if escalation is needed
        escalation_needed = requires_escalation(risk_level, intent)
        
        logger.info(f"Intent: {intent}, Risk: {risk_level}, Escalation: {escalation_needed}")
        
        return BankingResponse(
            response=response_text,
            intent=intent,
            risk_level=risk_level,
            requires_escalation=escalation_needed,
            compliance_check=compliance_result,
            timestamp=datetime.utcnow().isoformat(),
            session_id=f"SESSION_{chat.customer_id}_{datetime.utcnow().timestamp()}"
        )
    
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/verify-identity")
async def verify_identity(verification: IdentityVerification):
    """Verify customer identity for sensitive operations."""
    
    try:
        customer = CUSTOMER_DATABASE.get(verification.customer_id)
        
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        logger.info(f"Identity verification requested for {verification.customer_id}")
        
        # Simulate verification process
        if verification.verification_method == "security_questions":
            # In production, validate against stored answers
            verification_passed = len(verification.verification_data.get("answers", [])) > 0
        elif verification.verification_method == "otp":
            verification_passed = verification.verification_data.get("otp") == "123456"  # Mock
        else:
            verification_passed = False
        
        if verification_passed:
            customer["verified"] = True
            return {
                "status": "verified",
                "customer_id": verification.customer_id,
                "message": "Identity verified successfully."
            }
        else:
            return {
                "status": "failed",
                "customer_id": verification.customer_id,
                "message": "Identity verification failed. Please try again."
            }
    
    except Exception as e:
        logger.error(f"Error in identity verification: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/account/{account_id}/transactions")
async def get_transactions(account_id: str):
    """Retrieve account transactions."""
    
    if account_id not in ACCOUNT_DATABASE:
        raise HTTPException(status_code=404, detail="Account not found")
    
    transactions = TRANSACTIONS.get(account_id, [])
    account = ACCOUNT_DATABASE.get(account_id)
    
    return {
        "account_id": account_id,
        "account_type": account.get("account_type"),
        "balance": account.get("balance"),
        "transactions": transactions,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/account/{account_id}/balance")
async def get_balance(account_id: str):
    """Retrieve account balance."""
    
    account = ACCOUNT_DATABASE.get(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    return {
        "account_id": account_id,
        "balance": account.get("balance"),
        "status": account.get("status"),
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
