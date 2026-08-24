"""Knowledge Base and RAG for E-Commerce Support Agent"""

import logging
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class KnowledgeBase:
    """Manages knowledge base and RAG (Retrieval-Augmented Generation) for e-commerce support."""
    
    def __init__(self):
        self.faq_database = {}
        self.product_knowledge = {}
        self.policies = {}
        self.search_history = []
        self._initialize_knowledge_base()
    
    def _initialize_knowledge_base(self):
        """Initialize with sample knowledge base entries."""
        
        # FAQs
        self.faq_database = {
            "shipping_time": {
                "question": "How long does shipping take?",
                "answer": "Standard shipping takes 5-7 business days. Express shipping takes 2-3 business days.",
                "tags": ["shipping", "delivery", "time"],
                "category": "shipping"
            },
            "return_policy": {
                "question": "What is your return policy?",
                "answer": "Items can be returned within 30 days of purchase in original condition. Return shipping is free.",
                "tags": ["return", "refund", "policy"],
                "category": "returns"
            },
            "payment_methods": {
                "question": "What payment methods do you accept?",
                "answer": "We accept all major credit cards, PayPal, Apple Pay, and Google Pay.",
                "tags": ["payment", "credit card", "methods"],
                "category": "payment"
            },
            "tracking": {
                "question": "How do I track my order?",
                "answer": "You can track your order using the tracking number sent to your email after shipment.",
                "tags": ["tracking", "order", "shipment"],
                "category": "shipping"
            },
            "exchange": {
                "question": "Do you offer exchanges?",
                "answer": "Yes, we offer free exchanges within 30 days if you need a different size or color.",
                "tags": ["exchange", "size", "color"],
                "category": "returns"
            }
        }
        
        # Product Knowledge
        self.product_knowledge = {
            "widget_a": {
                "name": "Widget A",
                "description": "Premium quality widget for daily use",
                "price": "$29.99",
                "stock": "In stock",
                "specifications": {"color": ["Red", "Blue", "Green"], "size": ["S", "M", "L"]},
                "return_eligible": True
            },
            "gadget_x": {
                "name": "Gadget X",
                "description": "Advanced gadget with smart features",
                "price": "$99.99",
                "stock": "Limited stock",
                "specifications": {"color": ["Black", "Silver"], "warranty": "2 years"},
                "return_eligible": True
            },
            "device_pro": {
                "name": "Device Pro",
                "description": "Professional-grade device for experts",
                "price": "$199.99",
                "stock": "Out of stock",
                "specifications": {"color": ["Black"], "battery": "48 hours"},
                "return_eligible": True
            }
        }
        
        # Policies
        self.policies = {
            "warranty": "All products come with a 1-year limited warranty covering manufacturing defects.",
            "privacy": "We protect your personal information and never share it with third parties.",
            "shipping_free_threshold": "Free shipping on orders over $50.",
            "discount_policy": "Discounts are applied at checkout and cannot be combined with other offers."
        }
    
    def search_faq(self, query: str) -> List[Dict]:
        """Search FAQ database using keyword matching."""
        
        query_lower = query.lower()
        results = []
        
        for faq_id, faq_data in self.faq_database.items():
            # Check tags for matches
            for tag in faq_data["tags"]:
                if tag in query_lower:
                    results.append({
                        "id": faq_id,
                        "question": faq_data["question"],
                        "answer": faq_data["answer"],
                        "category": faq_data["category"],
                        "relevance": 0.9
                    })
                    break
        
        # Log search
        self._log_search(query, len(results))
        
        return results
    
    def get_product_info(self, product_name: str) -> Optional[Dict]:
        """Retrieve product information."""
        
        product_key = product_name.lower().replace(" ", "_")
        
        for key, product in self.product_knowledge.items():
            if key == product_key or product["name"].lower() == product_name.lower():
                return product
        
        return None
    
    def search_products(self, query: str) -> List[Dict]:
        """Search products by name or specification."""
        
        query_lower = query.lower()
        results = []
        
        for product_key, product in self.product_knowledge.items():
            if query_lower in product["name"].lower():
                results.append({
                    "id": product_key,
                    "name": product["name"],
                    "price": product["price"],
                    "stock": product["stock"],
                    "relevance": 0.95
                })
            elif any(query_lower in str(v).lower() for v in product["specifications"].values()):
                results.append({
                    "id": product_key,
                    "name": product["name"],
                    "price": product["price"],
                    "stock": product["stock"],
                    "relevance": 0.7
                })
        
        return results
    
    def get_policy(self, policy_type: str) -> Optional[str]:
        """Retrieve policy information."""
        
        return self.policies.get(policy_type.lower())
    
    def augment_response(self, intent: str, user_query: str) -> str:
        """Augment response with relevant knowledge."""
        
        augmented_info = ""
        
        # Search FAQ
        faq_results = self.search_faq(user_query)
        if faq_results:
            augmented_info += f"\n\nRelevant Information: {faq_results[0]['answer']}"
        
        # Search products if asking about products
        if any(word in user_query.lower() for word in ["product", "item", "buy", "available"]):
            product_results = self.search_products(user_query)
            if product_results:
                augmented_info += f"\n\nAvailable Products: {product_results[0]['name']} - {product_results[0]['price']}"
        
        return augmented_info
    
    def _log_search(self, query: str, result_count: int):
        """Log search queries for analytics."""
        
        search_log = {
            "timestamp": datetime.utcnow().isoformat(),
            "query": query,
            "result_count": result_count
        }
        self.search_history.append(search_log)
        logger.info(f"Knowledge Base Search: {query} - Found {result_count} results")
    
    def get_search_analytics(self) -> Dict:
        """Get search analytics."""
        
        if not self.search_history:
            return {"total_searches": 0}
        
        return {
            "total_searches": len(self.search_history),
            "unique_queries": len(set(s["query"] for s in self.search_history)),
            "average_results_per_search": sum(s["result_count"] for s in self.search_history) / len(self.search_history)
        }
    
    def add_faq_entry(self, question: str, answer: str, tags: List[str], category: str):
        """Add new FAQ entry to knowledge base."""
        
        faq_id = f"faq_{len(self.faq_database)}"
        self.faq_database[faq_id] = {
            "question": question,
            "answer": answer,
            "tags": tags,
            "category": category
        }
        logger.info(f"New FAQ added: {faq_id}")
    
    def add_product(self, name: str, description: str, price: str, stock: str, specifications: Dict):
        """Add new product to knowledge base."""
        
        product_key = name.lower().replace(" ", "_")
        self.product_knowledge[product_key] = {
            "name": name,
            "description": description,
            "price": price,
            "stock": stock,
            "specifications": specifications,
            "return_eligible": True
        }
        logger.info(f"New product added: {product_key}")
