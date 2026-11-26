from pydantic import BaseModel, ConfigDict, Field, model_validator
from datetime import date


# Schema for a batch inside an invoice request
# The invoice is set by the server, so no invoice_id here
class BatchInput(BaseModel):
    batch_number: str
    medicine_name: str
    quantity: int = Field(gt=0)
    manufacturing_date: date
    expiry_date: date

    # Expiry must be after manufacturing and in the future
    @model_validator(mode="after")
    def check_dates(self):
        if self.expiry_date <= self.manufacturing_date:
            raise ValueError(
                "Expiry date must be after manufacturing date"
            )
        if self.expiry_date <= date.today():
            raise ValueError("Expiry date must be in the future")
        return self


# Schema for creating a batch
class BatchCreate(BatchInput):
    invoice_id: int


# Schema for updating a batch
class BatchUpdate(BaseModel):
    batch_number: str | None = None
    medicine_name: str | None = None
    quantity: int | None = Field(default=None, gt=0)
    manufacturing_date: date | None = None
    expiry_date: date | None = None


# Schema for returning batch details
class BatchResponse(BaseModel):
    id: int
    batch_number: str
    medicine_name: str
    quantity: int
    manufacturing_date: date
    expiry_date: date
    invoice_id: int

    # Expiry check results, filled in by the endpoint
    checks: list[str] = []

    model_config = ConfigDict(from_attributes=True)
