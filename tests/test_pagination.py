# A list page over 100 rows is rejected on both list endpoints
def test_list_limit_capped_at_100(client, user_headers):
    invoices = client.get(
        "/invoices?limit=200", headers=user_headers
    )
    assert invoices.status_code == 422

    batches = client.get(
        "/batches?limit=200", headers=user_headers
    )
    assert batches.status_code == 422
