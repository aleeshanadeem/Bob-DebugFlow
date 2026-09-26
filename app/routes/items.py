"""
app/routes/items.py
-------------------
FastAPI router handling Item CRUD operations.

Endpoints:
    POST   /items/           Create a new item
    GET    /items/{item_id}  Retrieve a single item by ID
    GET    /items/           List items, optionally filtered by description
    DELETE /items/{item_id}  Delete an item by ID

This module contains two intentional bugs:
    B3 — The filter-by-description query uses a direct equality comparison
         on a nullable column without guarding against None values. Passing
         description=None as a query parameter triggers incorrect SQL that
         returns no results instead of all items (or raises a DB-level error
         depending on the driver).
    B4 — GET /items/{item_id} performs a dict-style lookup that raises an
         unhandled KeyError when the item does not exist, instead of
         returning a proper HTTP 404 response.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models import ItemORM, ItemCreate, ItemResponse
from app.utils import round_price

router = APIRouter(prefix="/items", tags=["items"])


@router.post("/", response_model=ItemResponse, status_code=201)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    """
    Create a new item record.

    The price is rounded before storage using the round_price() helper.
    Note: round_price() itself contains bug B5 (see app/utils.py).
    """
    db_item = ItemORM(
        title=item.title,
        description=item.description,
        price=round_price(item.price),
        owner_id=item.owner_id,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.get("/{item_id}", response_model=ItemResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    """Retrieve a single item by its numeric ID. Returns 404 if not found."""
    db_item = db.query(ItemORM).filter(ItemORM.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item


@router.get("/", response_model=list[ItemResponse])
def list_items(description: Optional[str] = None, db: Session = Depends(get_db)):
    """
    List all items, with an optional filter by exact description text.

    An optional exact-match filter on the description field. An empty or
    blank description parameter is treated as "no filter" so that all items
    are returned.
    """
    query = db.query(ItemORM)
    if description is not None and description.strip():
        query = query.filter(ItemORM.description == description)
    return query.all()


@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    """Delete an item by ID. Returns 204 No Content on success."""
    db_item = db.query(ItemORM).filter(ItemORM.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
