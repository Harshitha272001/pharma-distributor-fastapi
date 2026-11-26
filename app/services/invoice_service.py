from sqlalchemy.orm import Session

from app.models.invoice import Invoice
from app.models.batch import Batch
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate
from app.schemas.batch import BatchCreate, BatchInput


# Get an invoice using its ID
def get_invoice_by_id(db: Session, invoice_id: int):
    return db.query(Invoice).filter(Invoice.id == invoice_id).first()


# Get an invoice using its invoice number
def get_invoice_by_number(db: Session, invoice_number: str):
    return db.query(Invoice).filter(
        Invoice.invoice_number == invoice_number
    ).first()


# Get all invoices, optionally filtered by status
def get_all_invoices(
    db: Session,
    status: str | None = None,
    skip: int = 0,
    limit: int = 20
):
    query = db.query(Invoice)

    if status:
        query = query.filter(Invoice.status == status)

    return query.offset(skip).limit(limit).all()


# Create a new invoice
def create_invoice(db: Session, invoice_data: InvoiceCreate):

    # Check whether the invoice number already exists
    existing = get_invoice_by_number(db, invoice_data.invoice_number)

    if existing:
        raise ValueError("Invoice number already exists")

    # Save invoice to database
    new_invoice = Invoice(**invoice_data.model_dump())
    db.add(new_invoice)
    db.commit()
    db.refresh(new_invoice)

    return new_invoice


# Create an invoice along with its batches
def create_invoice_with_batches(
    db: Session,
    invoice_data: InvoiceCreate,
    batches_data: list[BatchInput]
):

    # Check the invoice number first, before saving anything
    existing_invoice = get_invoice_by_number(db, invoice_data.invoice_number)

    if existing_invoice:
        raise ValueError("Invoice number already exists")

    # Check every batch number first, so a duplicate stops the whole invoice
    for batch_data in batches_data:
        existing_batch = db.query(Batch).filter(
            Batch.batch_number == batch_data.batch_number
        ).first()

        if existing_batch:
            raise ValueError(
                f"Batch number {batch_data.batch_number} already exists"
            )

    # Save the invoice
    new_invoice = Invoice(**invoice_data.model_dump())
    db.add(new_invoice)
    db.flush()

    # Save each batch against the new invoice
    created_batches = []

    for batch_data in batches_data:
        batch_dict = batch_data.model_dump()
        batch_dict["invoice_id"] = new_invoice.id
        new_batch = Batch(**batch_dict)
        db.add(new_batch)
        created_batches.append(new_batch)

    db.commit()
    db.refresh(new_invoice)

    for batch in created_batches:
        db.refresh(batch)

    return new_invoice, created_batches


# Update an invoice
def update_invoice(
    db: Session,
    invoice_id: int,
    invoice_data: InvoiceUpdate
):

    invoice = get_invoice_by_id(db, invoice_id)

    if not invoice:
        return None

    # Get only fields supplied by the client
    update_data = invoice_data.model_dump(exclude_unset=True)

    # Check for duplicate invoice number
    new_number = update_data.get("invoice_number")

    if new_number and new_number != invoice.invoice_number:
        existing = get_invoice_by_number(db, new_number)

        if existing:
            raise ValueError("Invoice number already exists")

    # Update invoice fields
    for key, value in update_data.items():
        if value is not None:
            setattr(invoice, key, value)

    db.commit()
    db.refresh(invoice)

    return invoice


# Delete an invoice
def delete_invoice(db: Session, invoice_id: int):

    invoice = get_invoice_by_id(db, invoice_id)

    if not invoice:
        return None

    db.delete(invoice)
    db.commit()

    return invoice


# Counts for the admin report: invoices by status, batches by expiry
def get_report_counts(db: Session):
    from datetime import date, timedelta
    from app.models.batch import Batch

    near_expiry_date = date.today() + timedelta(days=90)

    return {
        "total_invoices": db.query(Invoice).count(),
        "approved_invoices": db.query(Invoice).filter(
            Invoice.status == "approved"
        ).count(),
        "rejected_invoices": db.query(Invoice).filter(
            Invoice.status == "rejected"
        ).count(),
        "pending_invoices": db.query(Invoice).filter(
            Invoice.status == "pending"
        ).count(),
        "total_batches": db.query(Batch).count(),
        "expired_batches": db.query(Batch).filter(
            Batch.expiry_date <= date.today()
        ).count(),
        "near_expiry_batches": db.query(Batch).filter(
            Batch.expiry_date > date.today(),
            Batch.expiry_date <= near_expiry_date
        ).count(),
    }
