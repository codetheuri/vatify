from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

# --- User Schemas ---

class UserBase(BaseModel):
    email: str
    full_name: str
    phone_number: Optional[str] = None
    id_number: Optional[str] = None
    kra_pin: Optional[str] = None
    business_name: Optional[str] = None
    tax_obligation: str = "Income Tax"

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int
    is_active: bool
    created_at: int
    updated_at: int

# --- Transaction Schemas ---

class TransactionRead(BaseModel):
    id: int
    date: datetime
    description: str
    amount: float
    tax_amount: float
    category: str
    transaction_type: str
    source: str
    reference_number: Optional[str] = None
    etims_validated: bool
    etims_invoice_number: Optional[str] = None
    is_excluded_from_etims: bool
    notes: Optional[str] = None
    created_at: int

# --- Rule Schemas ---

class RuleCreate(BaseModel):
    pattern: str
    category: str
    transaction_type: str

class RuleRead(RuleCreate):
    id: int
    is_active: bool
    created_at: int

# --- Dashboard & Reconciliation Schemas ---

class DashboardSummary(BaseModel):
    period: str
    totals: Dict[str, Dict[str, float]]
    compliance_risk_count: int
    unvalidated_sum: float

class NilFilingResponse(BaseModel):
    acknowledgement_number: str
    status: str
    message: str
