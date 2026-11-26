from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.line_item import (
    LineItemCreate,
    LineItemUpdate,
    LineItemResponse,
)
from app.services import line_item_service


# Create router instance
router = APIRouter(
    prefix="/line-items",
    tags=["Line Items"]
)


# Create a new line item
@router.post(
    "",
    response_model=LineItemResponse,
    status_code=status.HTTP_201_CREATED
)
def create_line_item(
    line_item_data: LineItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return line_item_service.create_line_item(db, line_item_data)


# List line items, optionally for one invoice
@router.get("", response_model=list[LineItemResponse])
def list_line_items(
    invoice_id: int | None = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if invoice_id:
        return line_item_service.get_line_items_by_invoice(db, invoice_id)

    return line_item_service.get_all_line_items(db, skip, limit)


# Get one line item
@router.get("/{line_item_id}", response_model=LineItemResponse)
def get_line_item(
    line_item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    line_item = line_item_service.get_line_item_by_id(db, line_item_id)

    if not line_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Line item not found"
        )

    return line_item


# Update a line item
@router.patch("/{line_item_id}", response_model=LineItemResponse)
def update_line_item(
    line_item_id: int,
    line_item_data: LineItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    line_item = line_item_service.update_line_item(
        db, line_item_id, line_item_data
    )

    if not line_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Line item not found"
        )

    return line_item


# Delete a line item
@router.delete("/{line_item_id}")
def delete_line_item(
    line_item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    line_item = line_item_service.delete_line_item(db, line_item_id)

    if not line_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Line item not found"
        )

    return {"message": "Line item deleted successfully"}
