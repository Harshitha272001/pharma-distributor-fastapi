from pydantic import BaseModel, ConfigDict, Field, model_validator


# Schema for creating an invoice line item
class LineItemCreate(BaseModel):
    medicine_name: str
    quantity: int = Field(gt=0)
    unit_price: float = Field(gt=0)
    total_price: float = Field(gt=0)
    invoice_id: int
    batch_id: int | None = None

    # Total price must equal quantity times unit price
    @model_validator(mode="after")
    def check_total(self):
        if self.total_price != self.quantity * self.unit_price:
            raise ValueError(
                "Total price must equal quantity times unit price"
            )
        return self


# Schema for updating an invoice line item
class LineItemUpdate(BaseModel):
    medicine_name: str | None = None
    quantity: int | None = Field(default=None, gt=0)
    unit_price: float | None = Field(default=None, gt=0)
    total_price: float | None = Field(default=None, gt=0)
    batch_id: int | None = None


# Schema for returning line item details
class LineItemResponse(BaseModel):
    id: int
    medicine_name: str
    quantity: int
    unit_price: float
    total_price: float
    invoice_id: int
    batch_id: int | None

    model_config = ConfigDict(from_attributes=True)
