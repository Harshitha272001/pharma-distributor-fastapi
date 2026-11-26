from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.batch import BatchCreate, BatchUpdate, BatchResponse
from app.services import batch_service


# Create router instance
router = APIRouter(
    prefix="/batches",
    tags=["Batches"]
)


# Add expiry checks to a batch response
def with_checks(batch):
    response = BatchResponse.model_validate(batch)
    response.checks = batch_service.check_batch(batch)
    return response


# Create a new batch
@router.post(
    "",
    response_model=BatchResponse,
    status_code=status.HTTP_201_CREATED
)
def create_batch(
    batch_data: BatchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    try:
        new_batch = batch_service.create_batch(db, batch_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )

    return with_checks(new_batch)


# List batches
@router.get("", response_model=list[BatchResponse])
def list_batches(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    batches = batch_service.get_all_batches(db, skip, limit)
    return [with_checks(batch) for batch in batches]


# Get one batch by its batch number, with expiry checks
@router.get("/{batch_no}", response_model=BatchResponse)
def get_batch(
    batch_no: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    batch = batch_service.get_batch_by_number(db, batch_no)

    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )

    return with_checks(batch)


# Update a batch
@router.patch("/{batch_id}", response_model=BatchResponse)
def update_batch(
    batch_id: int,
    batch_data: BatchUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    try:
        batch = batch_service.update_batch(db, batch_id, batch_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )

    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )

    return with_checks(batch)


# Delete a batch
@router.delete("/{batch_id}")
def delete_batch(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    batch = batch_service.delete_batch(db, batch_id)

    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )

    return {"message": "Batch deleted successfully"}
