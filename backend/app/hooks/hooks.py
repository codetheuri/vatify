# Place for model hooks or shared mixins
from app.common.base.base_model import BaseModel
from sqlmodel import Field

class SoftDeleteMixin(BaseModel):
    is_deleted: bool = Field(default=False)

    def soft_delete(self):
        self.is_deleted = True
