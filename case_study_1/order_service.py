"""Order Service for E-Commerce Support Agent"""

import logging
from enum import Enum
from typing import Dict, Optional, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    RETURNED = "returned"

class ReturnStatus(str, Enum):
    INITIATED = "initiated"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"

class OrderService:
    """Manages orders, returns, and refunds for e-commerce support."""
    
    def __init__(self):
        self.orders = {}
        self.returns = {}
        self.refunds = {}
        self.return_policy_days = 30
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Initialize with sample order data."""
        
        self.orders = {
            "ORDER_12345": {
                "customer_id": "customer_123",
                "status": OrderStatus.IN_TRANSIT.value,
                "items": [
                    {"product": "Widget A", "quantity": 2, "price": 29.99},
                    {"product": "Widget B", "quantity": 1, "price": 39.99}
                ],
                "total_amount": 99.97,
                "order_date": (datetime.utcnow() - timedelta(days=2)).isoformat(),
                "expected_delivery": (datetime.utcnow() + timedelta(days=2)).isoformat(),
                "tracking_number": "TRK123456789",
                "carrier": "FedEx",
                "shipping_address": "123 Main St, City, State 12345"
            },
            "ORDER_67890": {
                "customer_id": "customer_456",
                "status": OrderStatus.DELIVERED.value,
                "items": [
                    {"product": "Gadget X", "quantity": 1, "price": 99.99}
                ],
                "total_amount": 99.99,
                "order_date": (datetime.utcnow() - timedelta(days=10)).isoformat(),
                "delivery_date": (datetime.utcnow() - timedelta(days=3)).isoformat(),
                "tracking_number": "TRK987654321",
                "carrier": "UPS",
                "shipping_address": "456 Oak Ave, Town, State 67890"
            }
        }
    
    def get_order(self, order_id: str) -> Optional[Dict]:
        """Retrieve order details."""
        
        order = self.orders.get(order_id)
        if order:
            logger.info(f"Order retrieved: {order_id}")
        else:
            logger.warning(f"Order not found: {order_id}")
        
        return order
    
    def get_customer_orders(self, customer_id: str) -> List[Dict]:
        """Retrieve all orders for a customer."""
        
        customer_orders = [
            order for order in self.orders.values()
            if order["customer_id"] == customer_id
        ]
        
        logger.info(f"Retrieved {len(customer_orders)} orders for customer {customer_id}")
        return customer_orders
    
    def update_order_status(self, order_id: str, new_status: OrderStatus) -> bool:
        """Update order status."""
        
        if order_id not in self.orders:
            logger.error(f"Order not found: {order_id}")
            return False
        
        self.orders[order_id]["status"] = new_status.value
        logger.info(f"Order {order_id} status updated to {new_status.value}")
        return True
    
    def initiate_return(self, order_id: str, reason: str, items: Optional[List[str]] = None) -> Optional[Dict]:
        """Initiate a return request."""
        
        order = self.get_order(order_id)
        if not order:
            logger.error(f"Cannot return: Order {order_id} not found")
            return None
        
        # Check if order is eligible for return
        order_date = datetime.fromisoformat(order["order_date"])
        days_since_order = (datetime.utcnow() - order_date).days
        
        if days_since_order > self.return_policy_days:
            logger.warning(f"Return not eligible: {days_since_order} days since order")
            return {
                "status": "rejected",
                "reason": f"Order is {days_since_order} days old. Return policy is {self.return_policy_days} days."
            }
        
        # Create return request
        return_id = f"RET_{order_id}_{datetime.utcnow().timestamp()}"
        return_request = {
            "return_id": return_id,
            "order_id": order_id,
            "customer_id": order["customer_id"],
            "status": ReturnStatus.INITIATED.value,
            "reason": reason,
            "items": items or [item["product"] for item in order["items"]],
            "initiated_date": datetime.utcnow().isoformat(),
            "total_amount": order["total_amount"],
            "return_label_sent": True
        }
        
        self.returns[return_id] = return_request
        logger.info(f"Return initiated: {return_id}")
        
        return return_request
    
    def get_return_status(self, return_id: str) -> Optional[Dict]:
        """Get status of a return request."""
        
        return self.returns.get(return_id)
    
    def approve_return(self, return_id: str) -> bool:
        """Approve a return request."""
        
        if return_id not in self.returns:
            logger.error(f"Return not found: {return_id}")
            return False
        
        self.returns[return_id]["status"] = ReturnStatus.APPROVED.value
        logger.info(f"Return approved: {return_id}")
        return True
    
    def process_refund(self, return_id: str, refund_amount: Optional[float] = None) -> Optional[Dict]:
        """Process refund for approved return."""
        
        return_request = self.get_return_status(return_id)
        if not return_request:
            logger.error(f"Return not found: {return_id}")
            return None
        
        if return_request["status"] != ReturnStatus.APPROVED.value:
            logger.warning(f"Cannot refund: Return {return_id} status is {return_request['status']}")
            return None
        
        # Calculate refund amount
        final_refund_amount = refund_amount or return_request["total_amount"]
        
        refund_id = f"REF_{return_id}_{datetime.utcnow().timestamp()}"
        refund = {
            "refund_id": refund_id,
            "return_id": return_id,
            "order_id": return_request["order_id"],
            "customer_id": return_request["customer_id"],
            "amount": final_refund_amount,
            "status": "processed",
            "processed_date": datetime.utcnow().isoformat(),
            "refund_method": "original_payment_method"
        }
        
        self.refunds[refund_id] = refund
        self.returns[return_id]["status"] = ReturnStatus.COMPLETED.value
        self.returns[return_id]["refund_id"] = refund_id
        
        logger.info(f"Refund processed: {refund_id} for amount ${final_refund_amount}")
        
        return refund
    
    def get_refund_status(self, refund_id: str) -> Optional[Dict]:
        """Get refund status."""
        
        return self.refunds.get(refund_id)
    
    def cancel_order(self, order_id: str, reason: str = "") -> bool:
        """Cancel an order."""
        
        order = self.get_order(order_id)
        if not order:
            return False
        
        # Can only cancel pending or confirmed orders
        if order["status"] not in [OrderStatus.PENDING.value, OrderStatus.CONFIRMED.value]:
            logger.warning(f"Cannot cancel order {order_id}: status is {order['status']}")
            return False
        
        self.update_order_status(order_id, OrderStatus.CANCELLED)
        logger.info(f"Order cancelled: {order_id}. Reason: {reason}")
        
        return True
    
    def get_tracking_info(self, order_id: str) -> Optional[Dict]:
        """Get tracking information for an order."""
        
        order = self.get_order(order_id)
        if not order:
            return None
        
        tracking_info = {
            "order_id": order_id,
            "tracking_number": order.get("tracking_number"),
            "carrier": order.get("carrier"),
            "status": order["status"],
            "current_location": "In transit to destination",
            "expected_delivery": order.get("expected_delivery"),
            "last_update": datetime.utcnow().isoformat()
        }
        
        return tracking_info
    
    def get_return_eligibility(self, order_id: str) -> Dict:
        """Check if an order is eligible for return."""
        
        order = self.get_order(order_id)
        if not order:
            return {"eligible": False, "reason": "Order not found"}
        
        order_date = datetime.fromisoformat(order["order_date"])
        days_since_order = (datetime.utcnow() - order_date).days
        
        eligible = days_since_order <= self.return_policy_days
        
        return {
            "eligible": eligible,
            "days_since_order": days_since_order,
            "days_remaining": max(0, self.return_policy_days - days_since_order),
            "return_policy_days": self.return_policy_days
        }
