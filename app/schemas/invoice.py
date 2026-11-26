from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

from app.schemas.batch import BatchInput, BatchResponse


# Schema for creating an invoice
class InvoiceCreate(BaseModel):
    user_id: int | None = None
    invoice_number: str
    distributor_name: str
    invoice_date: datetime
    total_amount: float = Field(gt=0)
    status: str = "pending"


# Schema for creating an invoice along with its batches
class InvoiceWithBatchesCreate(BaseModel):
    invoice_number: str
    distributor_name: str
    invoice_date: datetime
    total_amount: float = Field(gt=0)
    batches: list[BatchInput] = []


# Schema for updating an invoice
class InvoiceUpdate(BaseModel):
    invoice_number: str | None = None
    distributor_name: str | None = None
    invoice_date: datetime | None = None
    total_amount: float | None = Field(default=None, gt=0)
    status: str | None = None


# Schema for returning invoice details
class InvoiceResponse(BaseModel):
    id: int
    user_id: int
    invoice_number: str
    distributor_name: str
    invoice_date: datetime
    total_amount: float
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Schema for returning one invoice with its batches and checks
class InvoiceDetailResponse(InvoiceResponse):
    batches: list[BatchResponse] = []
    checks: list[str] = []
