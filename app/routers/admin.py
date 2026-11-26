from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.dependencies import require_role
from app.models.user import User
from app.services import invoice_service


# Create router instance
router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


# Report counts: invoices by status, batches by expiry
@router.get("/reports")
def get_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    return invoice_service.get_report_counts(db)
