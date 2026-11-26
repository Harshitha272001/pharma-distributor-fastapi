from sqlalchemy.orm import Session

from app.models.qa_review import QAReview
from app.models.invoice import Invoice
from app.schemas.qa_review import QAReviewDecision


# Get all reviews for one invoice
def get_reviews_by_invoice(db: Session, invoice_id: int):
    return db.query(QAReview).filter(
        QAReview.invoice_id == invoice_id
    ).all()


# Create a QA review and update the invoice status
def create_review(
    db: Session,
    invoice_id: int,
    review_data: QAReviewDecision,
    reviewed_by: int
):

    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()

    if not invoice:
        return None

    # A reason is required when rejecting an invoice
    if review_data.review_status == "rejected" and not review_data.remarks:
        raise ValueError("A reason is required when rejecting an invoice")

    # Save the review
    new_review = QAReview(
        invoice_id=invoice_id,
        review_status=review_data.review_status,
        remarks=review_data.remarks,
        reviewed_by=reviewed_by
    )
    db.add(new_review)

    # Update the invoice status to match the decision
    invoice.status = review_data.review_status

    db.commit()
    db.refresh(new_review)
    db.refresh(invoice)

    return new_review
