from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class ESlipBase(SQLModel):
    eslip_number: str = Field(index=True, unique=True)
    amount: float
    expiry_date: Optional[datetime] = None
    status: str = Field(default="Pending") # Pending, Paid, Cancelled, Expired
    payment_registration_number: Optional[str] = Field(default=None, index=True)
    obligation_name: str
    tax_period: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)

class ESlip(ESlipBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    
    # Relationship back to User
    user: Optional["User"] = Relationship(back_populates="eslips")

class ESlipRead(ESlipBase):
    id: int
    user_id: int
    
    class Config:
        from_attributes = True

class ESlipCreate(ESlipBase):
    pass
