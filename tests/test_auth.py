# Register a new user
def test_register_user(client):
    response = client.post("/users/register", json={
        "name": "Harshitha",
        "email": "harshitha@test.com",
        "password": "password123",
    })

    assert response.status_code == 201
    assert response.json()["email"] == "harshitha@test.com"
    assert response.json()["role"] == "distributor"


# Registering the same email twice is a conflict
def test_register_duplicate_email(client):
    client.post("/users/register", json={
        "name": "Harshitha",
        "email": "duplicate@test.com",
        "password": "password123",
    })

    response = client.post("/users/register", json={
        "name": "Harshitha",
        "email": "duplicate@test.com",
        "password": "password123",
    })

    assert response.status_code == 409


# Login returns a bearer token
def test_login_success(client):
    client.post("/users/register", json={
        "name": "Harshitha",
        "email": "login@test.com",
        "password": "password123",
    })

    response = client.post("/auth/login", json={
        "email": "login@test.com",
        "password": "password123",
    })

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


# Wrong password means no token
def test_login_wrong_password(client):
    client.post("/users/register", json={
        "name": "Harshitha",
        "email": "wrongpass@test.com",
        "password": "password123",
    })

    response = client.post("/auth/login", json={
        "email": "wrongpass@test.com",
        "password": "notmypassword",
    })

    assert response.status_code == 401


# A logged-in user can see their own profile
def test_get_my_profile(client, user_headers):
    response = client.get("/users/me", headers=user_headers)

    assert response.status_code == 200
    assert response.json()["email"] == "user@test.com"


# No token means no profile
def test_get_my_profile_without_token(client):
    response = client.get("/users/me")

    assert response.status_code == 401


# A distributor cannot use the admin-only endpoint
def test_admin_endpoint_forbidden_for_distributor(client, user_headers):
    response = client.get("/users/admin-test", headers=user_headers)

    assert response.status_code == 403


# An admin can use the admin-only endpoint
def test_admin_endpoint_for_admin(client, admin_headers):
    response = client.get("/users/admin-test", headers=admin_headers)

    assert response.status_code == 200
    assert response.json()["message"] == "Welcome Admin!"
