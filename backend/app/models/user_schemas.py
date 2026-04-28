from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional

class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="The user's registered email address")
    password: str = Field(..., min_length=1, description="Password cannot be blank")

    @validator('email', 'password')
    def not_empty(cls, v):
        if isinstance(v, str) and not v.strip():
            raise ValueError("Field cannot be empty or just whitespace")
        return v

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")
    full_name: str = Field(..., min_length=2)
    phone_number: Optional[str] = None
    kra_pin: str = Field(..., min_length=11, max_length=11)

    @validator('full_name', 'kra_pin')
    def not_empty(cls, v):
        if not v.strip():
            raise ValueError("Field cannot be empty")
        return v

class UserVerify(BaseModel):
    token: str = Field(..., min_length=1)

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    phone_number: Optional[str] = None
    kra_pin: Optional[str] = None
    business_name: Optional[str] = None
    tax_obligations: Optional[str] = "Income Tax"
    
    # KRA Metadata
    kra_status: Optional[str] = "Active"
    pin_status: Optional[str] = "Active"
    physical_address: Optional[str] = None
    last_sync_at: Optional[int] = None
    
    mfa_enabled: bool = False
    is_verified: bool = False
    
    class Config:
        from_attributes = True
