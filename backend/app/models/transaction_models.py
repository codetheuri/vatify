from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Relationship, Field
from app.common.base.base_model import BaseModel

if TYPE_CHECKING:
    from .user_models import User

class TaxTransaction(BaseModel, table=True):
    date: datetime
    description: str
    amount: float
    tax_amount: float = Field(default=0.0) # For VAT components
    category: Optional[str] = "Uncategorized"
    transaction_type: str = Field(description="Income or Expense")
    source: str = Field(description="M-Pesa, Bank, or Manual")
    reference_number: Optional[str] = Field(default=None, index=True) # e.g. M-Pesa Receipt ID
    
    # eTIMS Fields
    etims_validated: bool = Field(default=False)
    etims_invoice_number: Optional[str] = Field(default=None, index=True)
    is_excluded_from_etims: bool = Field(default=False) # For Salaries, Bank interest, etc.
    
    notes: Optional[str] = None
    original_payload: Optional[str] = None # Raw data from CSV/SMS for audit trail
    
    user_id: int = Field(foreign_key="user.id")
    user: "User" = Relationship(back_populates="tax_transactions")

    document_id: Optional[int] = Field(default=None, foreign_key="taxdocument.id")
    document: Optional["TaxDocument"] = Relationship(
        back_populates="transactions",
        sa_relationship_kwargs={"foreign_keys": "[TaxTransaction.document_id]"}
    )

class CategoryRule(BaseModel, table=True):
    pattern: str = Field(description="Keyword or Regex to match in description")
    category: str
    transaction_type: str
    is_active: bool = Field(default=True)
    
    user_id: int = Field(foreign_key="user.id")
    user: "User" = Relationship(back_populates="rules")

class TaxPeriod(BaseModel, table=True):
    month: int
    year: int
    tax_type: str = Field(default="Income Tax") # VAT, TOT, MRI
    
    total_income: float = Field(default=0.0)
    total_expenses: float = Field(default=0.0)
    total_vat: float = Field(default=0.0)
    
    tax_payable: float = Field(default=0.0)
    tax_paid: float = Field(default=0.0)
    
    status: str = Field(default="Draft") # Draft, Calculated, Filed
    submission_reference: Optional[str] = None # KRA Acknowledgement Number
    
    user_id: int = Field(foreign_key="user.id")
    user: "User" = Relationship(back_populates="tax_periods")

class TaxDocument(BaseModel, table=True):
    filename: str
    file_path: str
    file_type: str # PDF, PNG, JPG
    document_type: str = Field(default="Invoice") # Invoice, Receipt, Credit Note
    
    # Extracted Data
    extracted_vendor: Optional[str] = None
    extracted_pin: Optional[str] = None
    extracted_invoice_number: Optional[str] = None
    extracted_date: Optional[datetime] = None
    extracted_amount: float = Field(default=0.0)
    extracted_tax_amount: float = Field(default=0.0)
    
    is_processed: bool = Field(default=False)
    
    user_id: int = Field(foreign_key="user.id")
    user: "User" = Relationship(back_populates="documents")
    
    # Link to transaction if matched (for single Invoices)
    transaction_id: Optional[int] = Field(default=None, foreign_key="taxtransaction.id")
    
    # Batch transactions if this was a CSV/M-Pesa upload
    transactions: List["TaxTransaction"] = Relationship(
        back_populates="document",
        sa_relationship_kwargs={"foreign_keys": "[TaxTransaction.document_id]"}
    )
