import pandas as pd
from io import BytesIO
from typing import List
from app.models.transaction_models import TaxTransaction

class ExporterService:
    @staticmethod
    def generate_itax_vat_csv(transactions: List[TaxTransaction], export_type: str = "purchases") -> BytesIO:
        """
        Generates a CSV formatted specifically for the iTax VAT return import.
        export_type: 'sales' or 'purchases'
        """
        data = []
        
        if export_type == "purchases":
            # iTax Purchase Sheet Layout (Simplified for the project)
            # PIN of Supplier, Name of Supplier, Invoice Number, Invoice Date, Description, Amount, VAT
            for tx in transactions:
                if tx.transaction_type == "Expense" and not tx.is_excluded_from_etims:
                    data.append({
                        "PIN of Supplier": "P000000000P", # In real life, we'd extract this from the invoice
                        "Name of Supplier": tx.description[:50],
                        "Invoice Number": tx.reference_number or "N/A",
                        "Invoice Date": tx.date.strftime("%d/%m/%Y"),
                        "Description of Goods": tx.category,
                        "Taxable Value": round(tx.amount / 1.16, 2),
                        "VAT Amount": round(tx.tax_amount, 2)
                    })
        else:
            # iTax Sales Sheet Layout
            for tx in transactions:
                if tx.transaction_type == "Income":
                    data.append({
                        "PIN of Customer": "N/A",
                        "Name of Customer": tx.description[:50],
                        "Invoice Number": tx.reference_number or "N/A",
                        "Invoice Date": tx.date.strftime("%d/%m/%Y"),
                        "Taxable Value": round(tx.amount / 1.16, 2),
                        "VAT Amount": round(tx.tax_amount, 2)
                    })

        df = pd.DataFrame(data)
        output = BytesIO()
        df.to_csv(output, index=False)
        output.seek(0)
        return output
