from typing import List, Optional, TYPE_CHECKING
from sqlmodel import Relationship, Field
from app.common.base.base_model import BaseModel

if TYPE_CHECKING:
    from .transaction_models import TaxTransaction, CategoryRule, TaxPeriod, TaxDocument
    from .eslip_models import ESlip

class User(BaseModel, table=True):
    email: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: str
    phone_number: Optional[str] = Field(default=None, index=True)
    id_number: Optional[str] = Field(default=None, index=True)
    kra_pin: Optional[str] = Field(default=None, index=True)
    business_name: Optional[str] = None
    tax_obligations: str = Field(default="Income Tax") # Comma separated: VAT, TOT, Income Tax
    
    # Enhanced KRA Metadata
    kra_status: Optional[str] = Field(default="Active")
    pin_status: Optional[str] = Field(default="Active")
    physical_address: Optional[str] = None
    last_sync_at: Optional[int] = None # Timestamp
    
    # Password Reset
    reset_token: Optional[str] = Field(default=None, index=True)
    reset_expiry: Optional[int] = None # Timestamp

    # Multi-factor Authentication
    mfa_enabled: bool = False
    mfa_secret: Optional[str] = None # For TOTP
    otp_code: Optional[str] = None   # For Email OTP
    otp_expiry: Optional[int] = None
    otp_resend_count: int = Field(default=0)
    last_otp_resend: Optional[int] = None # Timestamp
    
    # Session & Security
    refresh_token: Optional[str] = Field(default=None, index=True)
    is_verified: bool = Field(default=False)
    verification_token: Optional[str] = Field(default=None, index=True)
    
    is_active: bool = Field(default=True)

    tax_transactions: List["TaxTransaction"] = Relationship(back_populates="user")
    rules: List["CategoryRule"] = Relationship(back_populates="user")
    tax_periods: List["TaxPeriod"] = Relationship(back_populates="user")
    documents: List["TaxDocument"] = Relationship(back_populates="user")
    eslips: List["ESlip"] = Relationship(back_populates="user")
