"""Transaction Service for Banking Operations"""

import logging
from enum import Enum
from typing import Dict, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class TransactionStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REVERSED = "reversed"

class TransactionType(str, Enum):
    TRANSFER = "transfer"
    WITHDRAWAL = "withdrawal"
    DEPOSIT = "deposit"
    PURCHASE = "purchase"
    REFUND = "refund"

class TransactionService:
    """Manages banking transactions."""
    
    def __init__(self):
        self.transaction_history = {}
        self.pending_transactions = {}
    
    def create_transaction(self, customer_id: str, account_id: str, 
                          amount: float, transaction_type: TransactionType,
                          description: str) -> Dict:
        """Create a new transaction."""
        
        transaction = {
            "id": f"TXN_{customer_id}_{datetime.utcnow().timestamp()}",
            "customer_id": customer_id,
            "account_id": account_id,
            "amount": amount,
            "type": transaction_type.value,
            "description": description,
            "status": TransactionStatus.PENDING.value,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        self.pending_transactions[transaction["id"]] = transaction
        logger.info(f"Transaction created: {transaction['id']}")
        
        return transaction
    
    def get_transaction_status(self, transaction_id: str) -> Optional[Dict]:
        """Get status of a transaction."""
        
        # Check pending transactions
        if transaction_id in self.pending_transactions:
            return self.pending_transactions[transaction_id]
        
        # Check completed transactions
        if transaction_id in self.transaction_history:
            return self.transaction_history[transaction_id]
        
        return None
    
    def process_transaction(self, transaction_id: str) -> Dict:
        """Process a pending transaction."""
        
        if transaction_id not in self.pending_transactions:
            return {"status": "error", "message": "Transaction not found"}
        
        transaction = self.pending_transactions[transaction_id]
        transaction["status"] = TransactionStatus.PROCESSING.value
        transaction["updated_at"] = datetime.utcnow().isoformat()
        
        logger.info(f"Processing transaction: {transaction_id}")
        
        return transaction
    
    def complete_transaction(self, transaction_id: str) -> Dict:
        """Mark transaction as completed."""
        
        if transaction_id not in self.pending_transactions:
            return {"status": "error", "message": "Transaction not found"}
        
        transaction = self.pending_transactions.pop(transaction_id)
        transaction["status"] = TransactionStatus.COMPLETED.value
        transaction["completed_at"] = datetime.utcnow().isoformat()
        transaction["updated_at"] = datetime.utcnow().isoformat()
        
        self.transaction_history[transaction_id] = transaction
        logger.info(f"Transaction completed: {transaction_id}")
        
        return transaction
    
    def cancel_transaction(self, transaction_id: str, reason: str = "") -> Dict:
        """Cancel a pending transaction."""
        
        if transaction_id not in self.pending_transactions:
            return {"status": "error", "message": "Transaction not found"}
        
        transaction = self.pending_transactions.pop(transaction_id)
        transaction["status"] = TransactionStatus.FAILED.value
        transaction["cancellation_reason"] = reason
        transaction["updated_at"] = datetime.utcnow().isoformat()
        
        self.transaction_history[transaction_id] = transaction
        logger.info(f"Transaction cancelled: {transaction_id}")
        
        return transaction
    
    def get_pending_transactions(self, customer_id: str) -> list:
        """Get all pending transactions for a customer."""
        
        pending = [
            txn for txn in self.pending_transactions.values()
            if txn["customer_id"] == customer_id
        ]
        
        return pending
    
    def get_transaction_history(self, customer_id: str, days: int = 30) -> list:
        """Get transaction history for a customer."""
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        history = [
            txn for txn in self.transaction_history.values()
            if txn["customer_id"] == customer_id and 
            datetime.fromisoformat(txn["created_at"]) > cutoff_date
        ]
        
        return sorted(history, key=lambda x: x["created_at"], reverse=True)
    
    def detect_anomalies(self, customer_id: str) -> Dict:
        """Detect anomalies in transaction patterns."""
        
        history = self.get_transaction_history(customer_id, days=30)
        
        if not history:
            return {"anomalies_detected": False, "message": "Insufficient transaction history"}
        
        # Calculate average transaction amount
        amounts = [txn["amount"] for txn in history]
        avg_amount = sum(amounts) / len(amounts)
        
        # Check for outliers
        anomalies = []
        for txn in history:
            if txn["amount"] > avg_amount * 3:
                anomalies.append({
                    "transaction_id": txn["id"],
                    "amount": txn["amount"],
                    "reason": "Amount significantly higher than average"
                })
        
        # Check for rapid successive transactions
        if len(history) > 10:
            anomalies.append({
                "reason": "High transaction frequency detected"
            })
        
        return {
            "anomalies_detected": len(anomalies) > 0,
            "anomalies": anomalies,
            "average_transaction_amount": avg_amount
        }
