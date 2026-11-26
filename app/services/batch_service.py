from datetime import date

from sqlalchemy.orm import Session

from app.models.batch import Batch
from app.schemas.batch import BatchCreate, BatchUpdate


# Batches expiring within this many days count as near expiry
NEAR_EXPIRY_DAYS = 90


# Check a batch and list what is wrong with it
def check_batch(batch: Batch):
    checks = []
    today = date.today()

    if batch.expiry_date <= today:
        checks.append("expired")
    elif (batch.expiry_date - today).days < NEAR_EXPIRY_DAYS:
        checks.append("near_expiry")
    else:
        checks.append("valid")

    if batch.manufacturing_date >= batch.expiry_date:
        checks.append("expiry_before_manufacturing")

    return checks


# Get a batch using its ID
def get_batch_by_id(db: Session, batch_id: int):
    return db.query(Batch).filter(Batch.id == batch_id).first()


# Get a batch using its batch number
def get_batch_by_number(db: Session, batch_number: str):
    return db.query(Batch).filter(
        Batch.batch_number == batch_number
    ).first()


# Get all batches
def get_all_batches(db: Session, skip: int = 0, limit: int = 20):
    return db.query(Batch).offset(skip).limit(limit).all()


# Create a new batch
def create_batch(db: Session, batch_data: BatchCreate):

    # Check whether the batch number already exists
    existing = get_batch_by_number(db, batch_data.batch_number)

    if existing:
        raise ValueError("Batch number already exists")

    # Save batch to database
    new_batch = Batch(**batch_data.model_dump())
    db.add(new_batch)
    db.commit()
    db.refresh(new_batch)

    return new_batch


# Update a batch
def update_batch(db: Session, batch_id: int, batch_data: BatchUpdate):

    batch = get_batch_by_id(db, batch_id)

    if not batch:
        return None

    # Get only fields supplied by the client
    update_data = batch_data.model_dump(exclude_unset=True)

    # Check for duplicate batch number
    new_number = update_data.get("batch_number")

    if new_number and new_number != batch.batch_number:
        existing = get_batch_by_number(db, new_number)

        if existing:
            raise ValueError("Batch number already exists")

    # Update batch fields
    for key, value in update_data.items():
        if value is not None:
            setattr(batch, key, value)

    db.commit()
    db.refresh(batch)

    return batch


# Delete a batch
def delete_batch(db: Session, batch_id: int):

    batch = get_batch_by_id(db, batch_id)

    if not batch:
        return None

    db.delete(batch)
    db.commit()

    return batch
