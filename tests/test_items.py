"""
tests/test_items.py
-------------------
Tests for the /items/ route handlers and the price utility.

These tests are written against the *correct* expected behaviour.
They will FAIL against the current (buggy) application code and
must PASS once the bugs are fixed.

Bugs exercised here:
    B3 — list_items filter over nullable description returns wrong results
    B4 — get_item raises unhandled KeyError (500) instead of 404
    B5 — round_price() silently rounds to 1 decimal place instead of 2
"""

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _create_user(client, name="TestOwner", email=None):
    """Create a throwaway user and return its id."""
    if email is None:
        email = f"{name.lower().replace(' ', '')}@example.com"
    resp = client.post("/users/", json={"name": name, "email": email})
    return resp.json()["id"]


def _create_item(client, owner_id, title="Widget", description=None, price=9.99):
    """Create an item and return the full response body."""
    payload = {
        "title": title,
        "description": description,
        "price": price,
        "owner_id": owner_id,
    }
    resp = client.post("/items/", json=payload)
    assert resp.status_code == 201, f"Item creation failed: {resp.json()}"
    return resp.json()


# ---------------------------------------------------------------------------
# B4 — Unhandled KeyError on missing item
# ---------------------------------------------------------------------------

class TestGetItem:
    """Tests for GET /items/{item_id}"""

    def test_get_nonexistent_item_returns_404(self, client):
        """
        GET /items/99999 must return HTTP 404 Not Found.

        FAILS due to B4: the handler builds a dict of all items and accesses
        it by key. When the key is absent, Python raises a KeyError which
        propagates as a 500 Internal Server Error instead of a 404.
        """
        response = client.get("/items/99999")
        assert response.status_code == 404, (
            f"Expected 404 for missing item, got {response.status_code}. "
            "Bug B4: KeyError raised instead of HTTPException(404)."
        )

    def test_get_existing_item_returns_200(self, client):
        """GET /items/{id} returns 200 and correct body for a known item."""
        owner_id = _create_user(client, name="ItemOwner", email="itemowner@example.com")
        item = _create_item(client, owner_id=owner_id, title="Gadget", price=5.00)
        response = client.get(f"/items/{item['id']}")
        assert response.status_code == 200
        assert response.json()["title"] == "Gadget"


# ---------------------------------------------------------------------------
# B3 — Nullable description filter returns wrong results
# ---------------------------------------------------------------------------

class TestListItems:
    """Tests for GET /items/"""

    def test_list_items_empty_description_param_returns_all(self, client):
        """
        Passing ?description= (empty string) must return all items — it
        should be treated as "no filter applied".

        FAILS due to B3: the guard is `if description is not None`, which
        is True for an empty string. The route then executes
        WHERE description = '' which matches nothing, so an empty list is
        returned instead of all items.
        """
        owner_id = _create_user(client, name="ListOwner", email="listowner@example.com")
        _create_item(client, owner_id=owner_id, title="Gadget", description="blue", price=3.00)
        _create_item(client, owner_id=owner_id, title="Widget", description="red", price=2.00)

        # Empty string query param — should behave as no filter
        response = client.get("/items/?description=")
        assert response.status_code == 200
        items = response.json()
        titles = [i["title"] for i in items]
        assert len(items) >= 2, (
            f"Expected all items returned for empty description filter, "
            f"got {len(items)}: {titles}. "
            "Bug B3: empty string is not guarded, triggers WHERE description='' "
            "which silently excludes all items."
        )
        assert "Gadget" in titles, (
            f"'Gadget' missing from results: {titles}. Bug B3."
        )

    def test_list_items_filter_by_description(self, client):
        """
        Filtering by an exact non-empty description string must return only
        items with that description.
        """
        owner_id = _create_user(client, name="FilterOwner", email="filterowner@example.com")
        _create_item(client, owner_id=owner_id, title="Alpha", description="red", price=1.00)
        _create_item(client, owner_id=owner_id, title="Beta", description="blue", price=2.00)

        response = client.get("/items/?description=red")
        assert response.status_code == 200
        items = response.json()
        titles = [i["title"] for i in items]
        assert "Alpha" in titles
        assert "Beta" not in titles


# ---------------------------------------------------------------------------
# B5 — Price rounding silently truncates second decimal
# ---------------------------------------------------------------------------

class TestPriceRounding:
    """Tests for the round_price() utility via the item creation endpoint."""

    def test_price_rounded_to_two_decimal_places(self, client):
        """
        Prices must be stored and returned rounded to exactly 2 decimal
        places.

        FAILS due to B5: round_price() multiplies/divides by 10 instead of
        100, truncating to 1 decimal place. A price of 19.99 is stored as
        19.9 instead of 19.99.
        """
        owner_id = _create_user(client, name="PriceOwner", email="priceowner@example.com")
        item = _create_item(client, owner_id=owner_id, title="Expensive", price=19.99)

        stored_price = item["price"]
        assert stored_price == pytest.approx(19.99, abs=0.001), (
            f"Expected price 19.99, got {stored_price}. "
            "Bug B5: round_price() uses /10 instead of /100."
        )

    def test_price_rounding_preserves_cents(self, client):
        """
        A price like 4.55 must be stored as 4.55, not truncated to 4.5.

        FAILS due to B5 — same root cause.
        """
        owner_id = _create_user(client, name="CentsOwner", email="centsowner@example.com")
        item = _create_item(client, owner_id=owner_id, title="Cents", price=4.55)

        stored_price = item["price"]
        assert stored_price == pytest.approx(4.55, abs=0.001), (
            f"Expected price 4.55, got {stored_price}. "
            "Bug B5: second decimal digit silently truncated by round_price()."
        )

    def test_whole_number_price_unaffected(self, client):
        """A price with no fractional part must survive rounding unchanged."""
        owner_id = _create_user(client, name="WholeOwner", email="wholeowner@example.com")
        item = _create_item(client, owner_id=owner_id, title="Round", price=10.00)
        assert item["price"] == pytest.approx(10.00, abs=0.001)


# ---------------------------------------------------------------------------
# General item CRUD (should pass — not covering buggy paths)
# ---------------------------------------------------------------------------

class TestCreateItem:
    """Tests for POST /items/"""

    def test_create_item_returns_201(self, client):
        """POST /items/ must return 201 Created."""
        owner_id = _create_user(client, name="Creator", email="creator@example.com")
        payload = {"title": "Thing", "description": "a thing", "price": 5.0, "owner_id": owner_id}
        response = client.post("/items/", json=payload)
        assert response.status_code == 201

    def test_create_item_response_has_id(self, client):
        """POST /items/ response body must contain an assigned id."""
        owner_id = _create_user(client, name="Creator2", email="creator2@example.com")
        payload = {"title": "Gizmo", "description": None, "price": 3.0, "owner_id": owner_id}
        response = client.post("/items/", json=payload)
        assert "id" in response.json()
