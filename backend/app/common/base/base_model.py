import time
from sqlmodel import SQLModel, Field
from typing import Optional

class BaseModel(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: int = Field(
        default_factory=lambda: int(time.time()),
        nullable=False
    )
    updated_at: int = Field(
        default_factory=lambda: int(time.time()),
        nullable=False
    )
