import os

# Test settings must be set before the app is imported
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "test-secret-key"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.database.session import get_db
from app.main import app


# Test database, separate from the real one
TEST_DATABASE_URL = "sqlite:///./test.db"
test_engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine
)

# Create all tables once for the test run
Base.metadata.drop_all(bind=test_engine)
Base.metadata.create_all(bind=test_engine)


# Use the test database for every request
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


# Fresh tables for every test, so tests never share data
@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield


@pytest.fixture
def client():
    return TestClient(app)


# Register a user and return their login headers
def login_as(client, email, role="distributor"):
    client.post("/users/register", json={
        "name": "Test User",
        "email": email,
        "password": "password123",
        "role": role,
    })
    response = client.post("/auth/login", json={
        "email": email,
        "password": "password123",
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def user_headers(client):
    return login_as(client, "user@test.com")


@pytest.fixture
def qa_headers(client):
    return login_as(client, "qa@test.com", role="qa")


@pytest.fixture
def admin_headers(client):
    return login_as(client, "admin@test.com", role="admin")


@pytest.fixture
def invoice_data():
    return {
        "invoice_number": "INV-1001",
        "distributor_name": "Cipla",
        "invoice_date": "2026-01-10T00:00:00",
        "total_amount": 45000,
    }


@pytest.fixture
def batch_data():
    return {
        "batch_number": "PAR-2026-014",
        "medicine_name": "Paracetamol 500mg",
        "quantity": 10000,
        "manufacturing_date": "2026-01-10",
        "expiry_date": "2027-12-31",
        "invoice_id": 1,
    }
