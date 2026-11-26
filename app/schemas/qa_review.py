from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


# Schema for creating a QA review
class QAReviewCreate(BaseModel):
    invoice_id: int
    review_status: str = "pending"
    remarks: str | None = Field(default=None, max_length=500)


# Schema for the QA decision on an invoice
class QAReviewDecision(BaseModel):
    review_status: Literal["approved", "rejected"]
    remarks: str | None = Field(default=None, max_length=500)


# Schema for updating a QA review
class QAReviewUpdate(BaseModel):
    review_status: str | None = None
    remarks: str | None = Field(default=None, max_length=500)


# Schema for returning QA review details
class QAReviewResponse(BaseModel):
    id: int
    invoice_id: int
    review_status: str
    remarks: str | None
    reviewed_by: int | None
    reviewed_at: datetime

    model_config = ConfigDict(from_attributes=True)
