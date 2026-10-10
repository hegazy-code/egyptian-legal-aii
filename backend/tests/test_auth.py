def test_register_and_login(client):
    register_resp = client.post(
        "/auth/register",
        json={"email": "student@example.com", "password": "strongpass123", "full_name": "Test User"},
    )
    assert register_resp.status_code == 201
    body = register_resp.json()
    assert body["email"] == "student@example.com"
    assert "hashed_password" not in body

    login_resp = client.post(
        "/auth/login", json={"email": "student@example.com", "password": "strongpass123"}
    )
    assert login_resp.status_code == 200
    token_body = login_resp.json()
    assert token_body["token_type"] == "bearer"
    assert token_body["access_token"]


def test_duplicate_registration_rejected(client):
    client.post(
        "/auth/register",
        json={"email": "dupe@example.com", "password": "strongpass123"},
    )
    second = client.post(
        "/auth/register",
        json={"email": "dupe@example.com", "password": "strongpass123"},
    )
    assert second.status_code == 409


def test_login_wrong_password_rejected(client):
    client.post(
        "/auth/register",
        json={"email": "wrongpass@example.com", "password": "strongpass123"},
    )
    resp = client.post(
        "/auth/login", json={"email": "wrongpass@example.com", "password": "not-the-password"}
    )
    assert resp.status_code == 401


def test_protected_endpoint_requires_token(client):
    resp = client.get("/conversations")
    assert resp.status_code == 401
