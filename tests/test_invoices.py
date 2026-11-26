# Create an invoice
def test_create_invoice(client, user_headers, invoice_data):
    response = client.post(
        "/invoices", json=invoice_data, headers=user_headers
    )

    assert response.status_code == 201
    assert response.json()["invoice_number"] == "INV-1001"
    assert response.json()["status"] == "pending"


# The same invoice number twice is a conflict
def test_create_duplicate_invoice(client, user_headers, invoice_data):
    client.post("/invoices", json=invoice_data, headers=user_headers)

    response = client.post(
        "/invoices", json=invoice_data, headers=user_headers
    )

    assert response.status_code == 409


# Creating an invoice needs a login
def test_create_invoice_without_login(client, invoice_data):
    response = client.post("/invoices", json=invoice_data)

    assert response.status_code == 401


# List invoices
def test_list_invoices(client, user_headers, invoice_data):
    client.post("/invoices", json=invoice_data, headers=user_headers)

    response = client.get("/invoices", headers=user_headers)

    assert response.status_code == 200
    assert len(response.json()) >= 1


# Get one invoice with its batches and checks
def test_get_invoice_detail(client, user_headers, invoice_data):
    created = client.post(
        "/invoices", json=invoice_data, headers=user_headers
    ).json()

    response = client.get(
        f"/invoices/{created['id']}", headers=user_headers
    )

    assert response.status_code == 200
    assert response.json()["invoice_number"] == "INV-1001"
    assert response.json()["batches"] == []


# Unknown invoice id is a 404
def test_get_invoice_not_found(client, user_headers):
    response = client.get("/invoices/99999", headers=user_headers)

    assert response.status_code == 404


# Create an invoice with batches from JSON data
def test_create_invoice_with_batches(client, user_headers, invoice_data):
    payload = dict(invoice_data)
    payload["batches"] = [{
        "batch_number": "PAR-2026-020",
        "medicine_name": "Paracetamol 500mg",
        "quantity": 5000,
        "manufacturing_date": "2026-01-10",
        "expiry_date": "2027-12-31",
    }]

    response = client.post(
        "/invoices/text", json=payload, headers=user_headers
    )

    assert response.status_code == 201
    assert len(response.json()["batches"]) == 1
    assert response.json()["checks"] == ["valid"]


# A batch that expired before today is rejected
def test_create_invoice_with_expired_batch(
    client, user_headers, invoice_data
):
    payload = dict(invoice_data)
    payload["invoice_number"] = "INV-1002"
    payload["batches"] = [{
        "batch_number": "PAR-2020-001",
        "medicine_name": "Paracetamol 500mg",
        "quantity": 100,
        "manufacturing_date": "2020-01-10",
        "expiry_date": "2021-01-10",
    }]

    response = client.post(
        "/invoices/text", json=payload, headers=user_headers
    )

    assert response.status_code == 422


# QA can approve an invoice
def test_qa_approve_invoice(client, user_headers, qa_headers, invoice_data):
    created = client.post(
        "/invoices", json=invoice_data, headers=user_headers
    ).json()

    response = client.patch(
        f"/invoices/{created['id']}/review",
        json={"review_status": "approved", "remarks": "All checks passed"},
        headers=qa_headers,
    )

    assert response.status_code == 200
    assert response.json()["review_status"] == "approved"


# Rejecting without a reason is rejected
def test_qa_reject_without_reason(
    client, user_headers, qa_headers, invoice_data
):
    invoice_data["invoice_number"] = "INV-1003"
    created = client.post(
        "/invoices", json=invoice_data, headers=user_headers
    ).json()

    response = client.patch(
        f"/invoices/{created['id']}/review",
        json={"review_status": "rejected"},
        headers=qa_headers,
    )

    assert response.status_code == 422


# A distributor cannot approve an invoice, only QA can
def test_review_forbidden_for_distributor(
    client, user_headers, invoice_data
):
    invoice_data["invoice_number"] = "INV-1004"
    created = client.post(
        "/invoices", json=invoice_data, headers=user_headers
    ).json()

    response = client.patch(
        f"/invoices/{created['id']}/review",
        json={"review_status": "approved"},
        headers=user_headers,
    )

    assert response.status_code == 403


# The AI endpoint needs a key, so without one it says so
def test_ai_text_without_api_key(client, user_headers):
    response = client.post(
        "/invoices/ai-text",
        json={"text": "Invoice INV-1005 from Cipla, total 45000"},
        headers=user_headers,
    )

    assert response.status_code == 503


# PDF upload is refused until OCR is set up
def test_upload_pdf_refused(client, user_headers):
    response = client.post(
        "/invoices/upload",
        files={"file": ("invoice.pdf", b"fake pdf", "application/pdf")},
        headers=user_headers,
    )

    assert response.status_code == 400
