import pandas as pd
from datetime import datetime
from io import BytesIO
from typing import List, Dict
import pdfplumber
import re

class ParserService:
    @staticmethod
    def parse_mpesa_csv(file_path: str) -> List[Dict]:
        df = pd.read_csv(file_path)
        df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
        
        parsed_transactions = []
        for _, row in df.iterrows():
            date_str = row.get('completion_time') or row.get('date')
            if not date_str: continue
            
            try:
                date_obj = pd.to_datetime(date_str)
            except: continue
            
            details = str(row.get('details', 'No Details'))
            paid_in = float(str(row.get('paid_in', 0)).replace(',', '')) if pd.notnull(row.get('paid_in')) else 0
            withdrawn = float(str(row.get('withdrawn', 0)).replace(',', '')) if pd.notnull(row.get('withdrawn')) else 0
            
            if paid_in > 0:
                amount, tx_type = paid_in, "Income"
            elif withdrawn > 0:
                amount, tx_type = withdrawn, "Expense"
            else: continue
            
            parsed_transactions.append({
                "date": date_obj,
                "description": details,
                "amount": amount,
                "transaction_type": tx_type,
                "reference_number": row.get('receipt_no'),
                "source": "M-Pesa"
            })
        return parsed_transactions

    @staticmethod
    def parse_mpesa_pdf(file_path: str) -> List[Dict]:
        parsed_transactions = []
        pattern = re.compile(
            r'([A-Z0-9]{10})\s+'              # Receipt No
            r'(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})\s+' # Completion Time
            r'(.*?)\s+'                       # Details
            r'COMPLETED\s+'                   # Status
            r'([\d,]+\.\d{2})\s+'            # Paid In
            r'([\d,]+\.\d{2})\s+'               # Withdrawn
            r'([\d,]+\.\d{2})'                # Balance
        )

        try:
            with pdfplumber.open(file_path) as pdf:
                text = "\n".join([page.extract_text() or "" for page in pdf.pages])
        except Exception as e:
            return parsed_transactions

        for line in text.split('\n'):
            match = pattern.search(line)
            if match:
                receipt = match.group(1)
                date_str = match.group(2)
                details = match.group(3).strip()
                paid_in_str = match.group(4)
                withdrawn_str = match.group(5)
                
                try:
                    date_obj = pd.to_datetime(date_str)
                except:
                    continue
                    
                paid_in = float(paid_in_str.replace(',', '')) if paid_in_str else 0.0
                withdrawn = float(withdrawn_str.replace(',', '')) if withdrawn_str else 0.0
                
                if paid_in > 0:
                    amount, tx_type = paid_in, "Income"
                elif withdrawn > 0:
                    amount, tx_type = withdrawn, "Expense"
                else: continue
                
                parsed_transactions.append({
                    "date": date_obj,
                    "description": details,
                    "amount": amount,
                    "transaction_type": tx_type,
                    "reference_number": receipt,
                    "source": "M-Pesa (PDF)"
                })
        return parsed_transactions

class CategorizerService:
    @staticmethod
    def categorize(description: str, rules: List[any]) -> str:
        desc_lower = description.lower()
        
        for rule in rules:
            if rule.pattern.lower() in desc_lower:
                return rule.category
        
        system_rules = {
            "KPLC": "Utilities", "KENYA POWER": "Utilities", "NAIROBI WATER": "Utilities",
            "ZUKU": "Communication", "SAFARICOM": "Communication", "AIRTEL": "Communication",
            "SUPERMARKET": "Supplies", "NAIVAS": "Supplies", "CARREFOUR": "Supplies",
            "SHELL": "Transport", "TOTAL": "Transport", "UBER": "Transport", "BOLT": "Transport",
            "SALARY": "Income", "LOAN": "Finance",
        }
        
        for pattern, category in system_rules.items():
            if pattern.lower() in desc_lower:
                return category
                
        return "Uncategorized"
