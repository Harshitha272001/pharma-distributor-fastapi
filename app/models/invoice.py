from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database.base import Base
from sqlalchemy.orm import relationship

# Represents the invoices table in PostgreSQL
class Invoice(Base):
    __tablename__ = "invoices"

    # Unique ID for each invoice
    id = Column(Integer, primary_key=True, index=True)

    # ID of the user who uploaded this invoice
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Unique invoice number
    invoice_number = Column(String(100), unique=True, nullable=False, index=True)

    # Name of the distributor
    distributor_name = Column(String(150), nullable=False)

    # Date on which invoice was generated
    invoice_date = Column(DateTime, nullable=False)

    # Total invoice amount
    total_amount = Column(Float, nullable=False)

    # Invoice processing status (default: pending)
    status = Column(String(50), default="pending")

    # Automatically records the creation timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Connects each invoice to its uploading user
    user = relationship("User", back_populates="invoices")
    # Connects one invoice to multiple batches
    batches = relationship("Batch", back_populates="invoice")
    # Connects one invoice to multiple line items
    line_items = relationship("LineItem", back_populates="invoice")
    # Connects one invoice to multiple QA reviews
    qa_reviews = relationship("QAReview", back_populates="invoice")