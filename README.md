# pharma-distributor-fastapi

A backend API built with Python and FastAPI for a pharma distributor.
Staff upload supplier invoices and Certificates of Analysis, the system
checks batch numbers, expiry dates and duplicates, and QA approves or
rejects each invoice with a reason.

## What it does

- User registration and JWT login, with roles: admin, staff, qa, distributor
- Invoice CRUD, with status filter and pagination
- Batch CRUD, with expiry and near-expiry checks (near expiry is under 90 days)
- Line items for each invoice, with total price checked against quantity
- QA review: approve or reject an invoice, a reason is required on reject
- Admin report: invoice counts by status, batch counts by expiry
- AI invoice parsing: paste raw invoice text, the LLM returns JSON only,
  validated with Pydantic, one retry on validation failure
- File upload for .txt invoices (PDF and image upload needs OCR, not set up yet)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Fill in `.env` with your database URL, a secret key, and an LLM key
if you want to use the AI endpoint.

## Run

```bash
uvicorn app.main:app --reload
```

Swagger docs at http://127.0.0.1:8000/docs

## Tests

```bash
pytest
```

Tests use a local SQLite database, so no PostgreSQL is needed to run them.

## Project layout

- `app/main.py` - app setup and router registration
- `app/core/` - settings, password hashing, JWT, login dependencies
- `app/database/` - database connection and table setup
- `app/models/` - SQLAlchemy tables
- `app/schemas/` - Pydantic request and response shapes
- `app/services/` - database logic for each area
- `app/routers/` - API endpoints for each area
- `tests/` - pytest tests
