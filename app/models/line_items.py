from sqlalchemy import Column, Integer, Float, ForeignKey, String
from app.database.base import Base
from sqlalchemy.orm import relationship


# Represents individual items in an invoice
class LineItem(Base):
    __tablename__ = "line_items"

    # Unique ID for each line item
    id = Column(Integer, primary_key=True, index=True)

    # Medicine name
    medicine_name = Column(String(150), nullable=False)

    # Quantity of medicine ordered
    quantity = Column(Integer, nullable=False)

    # Price per unit
    unit_price = Column(Float, nullable=False)

    # Total price for this line item
    total_price = Column(Float, nullable=False)

    # Links the item to its invoice
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)

    # Links the item to its pharmaceutical batch
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=True)

    # Connects each line item to its invoice
    invoice = relationship("Invoice", back_populates="line_items")

    # Connects each line item to its pharmaceutical batch
    batch = relationship("Batch", back_populates="line_items")