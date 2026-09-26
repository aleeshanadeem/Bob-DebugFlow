"""
tests/test_users.py
-------------------
Tests for the /users/ route handlers.

These tests are written against the *correct* expected behaviour.
They will FAIL against the current (buggy) application code and
must PASS once the bugs are fixed.

Bugs exercised here:
    B1 — POST /users/ returns 200 instead of 201 Created
    B2 — Email field accepts invalid strings (no format validation)
"""


class TestCreateUser:
    """Tests for POST /users/"""

    def test_create_user_returns_201(self, client):
        """
        POST /users/ must return HTTP 201 Created when a new user is
        successfully persisted.

        FAILS due to B1: the endpoint currently returns 200 (FastAPI default)
        because no explicit status_code=201 is set on the route decorator.
        """
        payload = {"name": "Alice", "email": "alice@example.com"}
        response = client.post("/users/", json=payload)
        assert response.status_code == 201, (
            f"Expected 201 Created, got {response.status_code}. "
            "Bug B1: POST /users/ missing status_code=201 on route decorator."
        )

    def test_create_user_response_body(self, client):
        """POST /users/ must return the created user with an assigned id."""
        payload = {"name": "Bob", "email": "bob@example.com"}
        response = client.post("/users/", json=payload)
        body = response.json()
        assert "id" in body
        assert body["name"] == "Bob"
        assert body["email"] == "bob@example.com"

    def test_create_user_rejects_invalid_email(self, client):
        """
        POST /users/ must reject email values that are not valid email
        addresses, returning HTTP 422 Unprocessable Entity.

        FAILS due to B2: UserCreate uses `str` instead of `EmailStr`, so
        Pydantic accepts any string without email format validation.
        The endpoint currently returns 200/201 for 'not-an-email'.
        """
        payload = {"name": "Eve", "email": "not-an-email"}
        response = client.post("/users/", json=payload)
        assert response.status_code == 422, (
            f"Expected 422 for invalid email, got {response.status_code}. "
            "Bug B2: email field uses str instead of EmailStr in UserCreate."
        )

    def test_create_user_rejects_missing_at_symbol(self, client):
        """
        Email addresses without @ must be rejected with 422.

        FAILS due to B2 — same root cause as above.
        """
        payload = {"name": "Mallory", "email": "nodomain"}
        response = client.post("/users/", json=payload)
        assert response.status_code == 422, (
            f"Expected 422 for email without @, got {response.status_code}. "
            "Bug B2: no email format validation on UserCreate.email."
        )

    def test_duplicate_email_returns_400(self, client):
        """Creating two users with the same email must return 400."""
        payload = {"name": "Carol", "email": "carol@example.com"}
        client.post("/users/", json=payload)
        response = client.post("/users/", json=payload)
        assert response.status_code == 400


class TestGetUser:
    """Tests for GET /users/{user_id}"""

    def test_get_existing_user(self, client):
        """GET /users/{id} returns the correct user for a known ID."""
        created = client.post("/users/", json={"name": "Dave", "email": "dave@example.com"})
        user_id = created.json()["id"]
        response = client.get(f"/users/{user_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "Dave"

    def test_get_nonexistent_user_returns_404(self, client):
        """GET /users/99999 must return 404 for an unknown ID."""
        response = client.get("/users/99999")
        assert response.status_code == 404


class TestListUsers:
    """Tests for GET /users/"""

    def test_list_users_returns_list(self, client):
        """GET /users/ returns a JSON array."""
        response = client.get("/users/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
