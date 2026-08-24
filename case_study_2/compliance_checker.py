"""Compliance and Security Validation Module"""

import logging
from enum import Enum
from typing import Dict, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class ComplianceStandard(str, Enum):
    PCI_DSS = "pci_dss"
    GDPR = "gdpr"
    SOC_2 = "soc_2"
    HIPAA = "hipaa"

class ComplianceChecker:
    """Validates transactions and operations for compliance."""
    
    def __init__(self):
        self.standards = [ComplianceStandard.PCI_DSS, ComplianceStandard.GDPR]
        self.audit_log = []
    
    def check_pci_dss_compliance(self, transaction_data: Dict) -> Tuple[bool, str]:
        """Check PCI-DSS Level 1 compliance."""
        
        # Check if card data is being handled
        if "card" in str(transaction_data).lower():
            # Ensure card data is tokenized, not stored in plain text
            if "card_number" in transaction_data:
                logger.warning("PCI-DSS: Card number found in plain text!")
                return False, "Card data must be tokenized"
        
        # Check encryption status
        if transaction_data.get("encrypted") != True:
            return False, "Transaction must be encrypted"
        
        logger.info("PCI-DSS compliance check: PASSED")
        return True, "PCI-DSS compliant"
    
    def check_gdpr_compliance(self, customer_data: Dict) -> Tuple[bool, str]:
        """Check GDPR data protection compliance."""
        
        # Check for consent
        if not customer_data.get("consent_provided"):
            return False, "GDPR: Customer consent required"
        
        # Check data retention policy
        if customer_data.get("retention_days", 0) > 2555:  # ~7 years
            return False, "Data retention exceeds GDPR guidelines"
        
        logger.info("GDPR compliance check: PASSED")
        return True, "GDPR compliant"
    
    def check_transaction_limits(self, amount: float, transaction_type: str) -> Tuple[bool, str]:
        """Validate transaction limits."""
        
        # Define limits based on transaction type
        daily_limits = {
            "transfer": 50000.00,
            "withdrawal": 10000.00,
            "purchase": 25000.00
        }
        
        limit = daily_limits.get(transaction_type, 10000.00)
        
        if amount > limit:
            logger.warning(f"Transaction exceeds limit: {amount} > {limit}")
            return False, f"Amount exceeds {transaction_type} limit of ${limit:.2f}"
        
        return True, "Transaction amount within limits"
    
    def check_fraud_indicators(self, transaction_data: Dict) -> Tuple[bool, str]:
        """Check for potential fraud indicators."""
        
        risk_score = 0
        
        # Check for unusual amount
        if transaction_data.get("amount", 0) > 5000:
            risk_score += 20
        
        # Check for unusual time
        hour = datetime.utcnow().hour
        if hour < 6 or hour > 23:  # Off-hours transaction
            risk_score += 15
        
        # Check for multiple transactions in short time
        if transaction_data.get("transactions_today", 0) > 5:
            risk_score += 25
        
        if risk_score > 50:
            return False, f"Fraud risk detected (score: {risk_score})"
        
        return True, "No fraud indicators detected"
    
    def audit_log_entry(self, customer_id: str, action: str, result: str):
        """Log compliance action for audit purposes."""
        
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "customer_id": customer_id,
            "action": action,
            "result": result
        }
        self.audit_log.append(entry)
        logger.info(f"Audit Log: {entry}")
    
    def validate_all_standards(self, transaction_data: Dict) -> Dict:
        """Run all compliance checks."""
        
        results = {}
        
        # PCI-DSS Check
        pci_passed, pci_msg = self.check_pci_dss_compliance(transaction_data)
        results["pci_dss"] = {"passed": pci_passed, "message": pci_msg}
        
        # GDPR Check
        gdpr_passed, gdpr_msg = self.check_gdpr_compliance(transaction_data.get("customer_data", {}))
        results["gdpr"] = {"passed": gdpr_passed, "message": gdpr_msg}
        
        # Transaction Limits Check
        limits_passed, limits_msg = self.check_transaction_limits(
            transaction_data.get("amount", 0),
            transaction_data.get("type", "purchase")
        )
        results["transaction_limits"] = {"passed": limits_passed, "message": limits_msg}
        
        # Fraud Check
        fraud_passed, fraud_msg = self.check_fraud_indicators(transaction_data)
        results["fraud_check"] = {"passed": fraud_passed, "message": fraud_msg}
        
        # Overall result
        all_passed = all(check["passed"] for check in results.values())
        
        return {
            "overall_compliant": all_passed,
            "checks": results,
            "timestamp": datetime.utcnow().isoformat()
        }
