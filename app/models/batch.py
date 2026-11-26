from sqlalchemy import Column, Integer, String, Date, ForeignKey
from app.database.base import Base
from sqlalchemy.orm import relationship

# Represents pharmaceutical batch details
class Batch(Base):
    __tablename__ = "batches"

    # Unique ID for each batch
    id = Column(Integer, primary_key=True, index=True)

    # Batch identification number
    batch_number = Column(String(100), unique=True, nullable=False, index=True)

    # Name of the medicine
    medicine_name = Column(String(150), nullable=False)

    # Quantity available in this batch
    quantity = Column(Integer, nullable=False)

    # Manufacturing date
    manufacturing_date = Column(Date, nullable=False)

    # Expiry date
    expiry_date = Column(Date, nullable=False)

    # ID of the invoice associated with this batch
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)

    # Connects each batch to its invoice
    invoice = relationship("Invoice", back_populates="batches")

    # Connects a batch to multiple line items
    line_items = relationship("LineItem", back_populates="batch")