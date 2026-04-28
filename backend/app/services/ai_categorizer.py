import re
from typing import List, Dict, Optional

class AiCategorizer:
    """
    AI-driven categorization service for Kenyan SME transactions.
    Uses pattern recognition and context-aware rules to map M-Pesa 
    descriptions to tax categories.
    """
    
    CATEGORIES = {
        "Taxes": [
            "kra", "tax", "vat", "excise", "stamp duty", "withholding", "itax", "customs"
        ],
        "Utilities": [
            "kplc", "kenya power", "nairobi water", "electricity", "sewerage", "garbage", "payment to kplc"
        ],
        "Supplies": [
            "quickmart", "naivas", "carrefour", "tuskys", "chandarana", "supermarket",
            "jumia", "copia", "glacier", "distributor", "wholesaler", "bakery", "butchery"
        ],
        "Communication": [
            "safaricom", "airtel", "telkom", "zuku", "faiba", "liquid", "internet", "airtime", "bundle"
        ],
        "Transport": [
            "shell", "total", "rubis", "uber", "bolt", "little cab", "petrol", "fuel", "matatu", "fines", "parking", "ncc"
        ],
        "Finance": [
            "bank", "transfer", "equity", "kcb", "m-shwari", "kcb mpesa", "interest", "loan", "repayment", "overdraft"
        ],
        "Salary": [
            "salary", "wage", "stipend", "kazi", "remuneration", "payroll"
        ],
        "Rent": [
            "rent", "landlord", "real estate", "property", "service charge", "apartment"
        ],
        "Marketing": [
            "facebook", "google", "ads", "instagram", "marketing", "promotion", "printing", "graphic"
        ],
        "Consultancy": [
            "lawyer", "advocate", "accountant", "audit", "consultant", "fiverr", "upwork"
        ]
    }

    @classmethod
    def categorize(cls, description: str, user_rules: List = None) -> str:
        """
        Main entry point for AI categorization.
        Order of precedence:
        1. User-defined rules (exact match)
        2. Pattern matching (AI Heuristics)
        3. Generic categorization
        """
        if not description:
            return "Uncategorized"

        cleaned_desc = cls._clean_description(description)
        
        # 1. Check User Rules first
        if user_rules:
            for rule in user_rules:
                if rule.pattern.lower() in cleaned_desc:
                    return rule.category

        # 2. AI Heuristic Matching
        for category, keywords in cls.CATEGORIES.items():
            for word in keywords:
                if word in cleaned_desc:
                    # Contextual override for M-Pesa specific patterns
                    if category == "Communication" and "airtime" in cleaned_desc:
                        return "Communication"
                    return category

        # 3. Handle M-Pesa Till/Paybill patterns
        if "buy goods" in cleaned_desc or "paybill" in cleaned_desc:
            # If we see a common business suffix like 'ltd', 'investments', 'enterprises'
            if any(suffix in cleaned_desc for suffix in ["ltd", "investments", "ent", "hms", "ventures"]):
                return "Supplies"

        return "General Expense"

    @staticmethod
    def _clean_description(description: str) -> str:
        """Removes transaction IDs and dates from description for better matching"""
        # Remove typical M-Pesa codes (e.g., SAK4... )
        desc = re.sub(r'^[A-Z0-9]{10}\b', '', description)
        # Remove timestamps/dates
        desc = re.sub(r'\d{2}/\d{2}/\d{2}', '', desc)
        return desc.lower().strip()
