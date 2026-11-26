from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.user import User
from app.schemas.qa_review import QAReviewDecision, QAReviewResponse
from app.services import qa_review_service


# Create router instance
router = APIRouter(
    prefix="/invoices",
    tags=["QA Reviews"]
)


# QA approves or rejects an invoice
@router.patch(
    "/{invoice_id}/review",
    response_model=QAReviewResponse
)
def review_invoice(
    invoice_id: int,
    review_data: QAReviewDecision,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("qa"))
):

    try:
        review = qa_review_service.create_review(
            db, invoice_id, review_data, current_user.id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(e)
        )

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )

    return review


# List all QA reviews for one invoice
@router.get(
    "/{invoice_id}/reviews",
    response_model=list[QAReviewResponse]
)
def list_reviews(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return qa_review_service.get_reviews_by_invoice(db, invoice_id)
