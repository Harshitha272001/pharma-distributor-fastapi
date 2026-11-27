from fastapi import APIRouter, Depends, File, HTTPException, Query, status, UploadFile
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.dependencies import get_current_user
from app.models.batch import Batch
from app.models.user import User
from app.schemas.invoice import (
    InvoiceCreate,
    InvoiceUpdate,
    InvoiceResponse,
    InvoiceWithBatchesCreate,
    InvoiceDetailResponse,
)
from app.schemas.batch import BatchCreate, BatchResponse
from app.services import invoice_service, batch_service
from app.services.llm_service import (
    parse_invoice_text,
    LLMNotConfiguredError,
    LLMRequestError,
    LLMParseError,
)


# Create router instance
router = APIRouter(
    prefix="/invoices",
    tags=["Invoices"]
)


# Build the detail response for one invoice
def build_detail_response(db: Session, invoice):
    batches = db.query(Batch).filter(
        Batch.invoice_id == invoice.id
    ).all()

    batch_responses = []
    all_checks = []

    for batch in batches:
        checks = batch_service.check_batch(batch)
        batch_response = BatchResponse.model_validate(batch)
        batch_response.checks = checks
        batch_responses.append(batch_response)
        all_checks.extend(checks)

    detail = InvoiceDetailResponse.model_validate(invoice)
    detail.batches = batch_responses
    detail.checks = sorted(set(all_checks))

    return detail


# Create a new invoice
@router.post(
    "",
    response_model=InvoiceResponse,
    status_code=status.HTTP_201_CREATED
)
def create_invoice(
    invoice_data: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # The invoice belongs to the logged-in user
    invoice_data.user_id = current_user.id

    # A new invoice always starts as pending
    invoice_data.status = "pending"

    try:
        return invoice_service.create_invoice(db, invoice_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


# Create an invoice along with its batches from JSON data
@router.post(
    "/text",
    response_model=InvoiceDetailResponse,
    status_code=status.HTTP_201_CREATED
)
def create_invoice_from_text(
    invoice_data: InvoiceWithBatchesCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Build the invoice from the request, owned by the logged-in user
    invoice_create = InvoiceCreate(
        user_id=current_user.id,
        invoice_number=invoice_data.invoice_number,
        distributor_name=invoice_data.distributor_name,
        invoice_date=invoice_data.invoice_date,
        total_amount=invoice_data.total_amount,
        status="pending"
    )

    try:
        new_invoice, _ = invoice_service.create_invoice_with_batches(
            db, invoice_create, invoice_data.batches
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )

    return build_detail_response(db, new_invoice)


# Create an invoice by letting the LLM read raw invoice text
@router.post(
    "/ai-text",
    response_model=InvoiceDetailResponse,
    status_code=status.HTTP_201_CREATED
)
def create_invoice_from_ai_text(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    text = payload.get("text", "")

    if not text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Invoice text is required"
        )

    # Ask the LLM to extract invoice data from the text
    try:
        parsed = parse_invoice_text(text)
    except LLMNotConfiguredError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except LLMRequestError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e)
        )
    except LLMParseError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(e)
        )

    # Build the invoice from what the LLM extracted
    invoice_create = InvoiceCreate(
        user_id=current_user.id,
        invoice_number=parsed.invoice_number,
        distributor_name=parsed.distributor_name,
        invoice_date=parsed.invoice_date,
        total_amount=parsed.total_amount,
        status="pending"
    )

    try:
        new_invoice, _ = invoice_service.create_invoice_with_batches(
            db, invoice_create, parsed.batches
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )

    return build_detail_response(db, new_invoice)


# Upload an invoice file
@router.post(
    "/upload",
    response_model=InvoiceDetailResponse,
    status_code=status.HTTP_201_CREATED
)
async def upload_invoice(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # PDF and image upload needs OCR, which is not set up yet
    if not file.filename.endswith(".txt"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Only .txt files are supported for now. "
                "PDF and image upload needs OCR, which is not set up yet."
            )
        )

    # Read the text file and parse it with the LLM
    content = await file.read()
    text = content.decode("utf-8")

    return create_invoice_from_ai_text(
        {"text": text}, db, current_user
    )


# List invoices, optionally filtered by status
@router.get("", response_model=list[InvoiceResponse])
def list_invoices(
    status: str | None = None,
    skip: int = 0,
    # A page never returns more than 100 rows
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return invoice_service.get_all_invoices(db, status, skip, limit)


# Get one invoice with its batches and checks
@router.get("/{invoice_id}", response_model=InvoiceDetailResponse)
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    invoice = invoice_service.get_invoice_by_id(db, invoice_id)

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )

    return build_detail_response(db, invoice)


# Update an invoice
@router.patch("/{invoice_id}", response_model=InvoiceResponse)
def update_invoice(
    invoice_id: int,
    invoice_data: InvoiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    try:
        invoice = invoice_service.update_invoice(
            db, invoice_id, invoice_data
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )

    return invoice


# Delete an invoice
@router.delete("/{invoice_id}")
def delete_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    invoice = invoice_service.delete_invoice(db, invoice_id)

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )

    return {"message": "Invoice deleted successfully"}
