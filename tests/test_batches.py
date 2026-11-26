# Create a batch
def test_create_batch(client, user_headers, invoice_data, batch_data):
    invoice = client.post(
        "/invoices", json=invoice_data, headers=user_headers
    ).json()
    batch_data["invoice_id"] = invoice["id"]

    response = client.post(
        "/batches", json=batch_data, headers=user_headers
    )

    assert response.status_code == 201
    assert response.json()["batch_number"] == "PAR-2026-014"
    assert response.json()["checks"] == ["valid"]


# The same batch number twice is a conflict
def test_create_duplicate_batch(
    client, user_headers, invoice_data, batch_data
):
    invoice = client.post(
        "/invoices", json=invoice_data, headers=user_headers
    ).json()
    batch_data["invoice_id"] = invoice["id"]

    client.post("/batches", json=batch_data, headers=user_headers)

    response = client.post(
        "/batches", json=batch_data, headers=user_headers
    )

    assert response.status_code == 409


# Expiry before manufacturing is rejected
def test_create_batch_expiry_before_manufacturing(
    client, user_headers, invoice_data, batch_data
):
    invoice = client.post(
        "/invoices", json=invoice_data, headers=user_headers
    ).json()
    batch_data["invoice_id"] = invoice["id"]
    batch_data["batch_number"] = "PAR-2026-030"
    batch_data["manufacturing_date"] = "2026-06-10"
    batch_data["expiry_date"] = "2026-01-10"

    response = client.post(
        "/batches", json=batch_data, headers=user_headers
    )

    assert response.status_code == 422


# A batch that already expired is rejected
def test_create_expired_batch(
    client, user_headers, invoice_data, batch_data
):
    invoice = client.post(
        "/invoices", json=invoice_data, headers=user_headers
    ).json()
    batch_data["invoice_id"] = invoice["id"]
    batch_data["batch_number"] = "PAR-2020-002"
    batch_data["manufacturing_date"] = "2020-01-10"
    batch_data["expiry_date"] = "2021-01-10"

    response = client.post(
        "/batches", json=batch_data, headers=user_headers
    )

    assert response.status_code == 422


# Get a batch by its number, with expiry checks
def test_get_batch_by_number(
    client, user_headers, invoice_data, batch_data
):
    invoice = client.post(
        "/invoices", json=invoice_data, headers=user_headers
    ).json()
    batch_data["invoice_id"] = invoice["id"]
    client.post("/batches", json=batch_data, headers=user_headers)

    response = client.get(
        "/batches/PAR-2026-014", headers=user_headers
    )

    assert response.status_code == 200
    assert response.json()["medicine_name"] == "Paracetamol 500mg"
    assert "valid" in response.json()["checks"]


# Unknown batch number is a 404
def test_get_batch_not_found(client, user_headers):
    response = client.get("/batches/NO-SUCH-BATCH", headers=user_headers)

    assert response.status_code == 404
