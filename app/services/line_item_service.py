from sqlalchemy.orm import Session

from app.models.line_items import LineItem
from app.schemas.line_item import LineItemCreate, LineItemUpdate


# Get a line item using its ID
def get_line_item_by_id(db: Session, line_item_id: int):
    return db.query(LineItem).filter(LineItem.id == line_item_id).first()


# Get all line items for one invoice
def get_line_items_by_invoice(db: Session, invoice_id: int):
    return db.query(LineItem).filter(
        LineItem.invoice_id == invoice_id
    ).all()


# Get all line items
def get_all_line_items(db: Session, skip: int = 0, limit: int = 20):
    return db.query(LineItem).offset(skip).limit(limit).all()


# Create a new line item
def create_line_item(db: Session, line_item_data: LineItemCreate):

    # Save line item to database
    new_line_item = LineItem(**line_item_data.model_dump())
    db.add(new_line_item)
    db.commit()
    db.refresh(new_line_item)

    return new_line_item


# Update a line item
def update_line_item(
    db: Session,
    line_item_id: int,
    line_item_data: LineItemUpdate
):

    line_item = get_line_item_by_id(db, line_item_id)

    if not line_item:
        return None

    # Get only fields supplied by the client
    update_data = line_item_data.model_dump(exclude_unset=True)

    # Update line item fields
    for key, value in update_data.items():
        if value is not None:
            setattr(line_item, key, value)

    db.commit()
    db.refresh(line_item)

    return line_item


# Delete a line item
def delete_line_item(db: Session, line_item_id: int):

    line_item = get_line_item_by_id(db, line_item_id)

    if not line_item:
        return None

    db.delete(line_item)
    db.commit()

    return line_item
