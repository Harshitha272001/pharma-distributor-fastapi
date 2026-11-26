from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database.base import Base
from sqlalchemy.orm import relationship


# Represents quality assurance review results
class QAReview(Base):
    __tablename__ = "qa_reviews"

    # Unique ID for each review
    id = Column(Integer, primary_key=True, index=True)

    # Links the review to an invoice
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)

    # Review result: approved, rejected, or pending
    review_status = Column(String(50), default="pending")

    # Comments or remarks from the reviewer
    remarks = Column(String(500), nullable=True)

    # ID of the QA user who reviewed this invoice
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Automatically records when the review was created
    reviewed_at = Column(DateTime(timezone=True), server_default=func.now())

    # Connects each QA review to its invoice
    invoice = relationship("Invoice", back_populates="qa_reviews")