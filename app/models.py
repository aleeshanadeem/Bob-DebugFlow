"""
app/models.py
-------------
SQLAlchemy ORM table definitions and Pydantic request/response schemas
for the two domain entities used in this sample app: User and Item.

ORM models define the database schema.
Pydantic models define the API contract (request bodies and responses).
"""

from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel, EmailStr
from typing import Optional

from app.database import Base


# ---------------------------------------------------------------------------
# ORM Models (SQLAlchemy)
# ---------------------------------------------------------------------------

class UserORM(Base):
    """Represents a registered user in the system."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)

    items = relationship("ItemORM", back_populates="owner")


class ItemORM(Base):
    """Represents a product item owned by a user."""

    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)   # Nullable — relevant to B3
    price = Column(Float, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("UserORM", back_populates="items")


# ---------------------------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------------------------

class UserCreate(BaseModel):
    """Request body for creating a new user.

    The email field uses EmailStr so Pydantic validates the format and
    returns 422 Unprocessable Entity for non-email strings.
    """
    name: str
    email: EmailStr


class UserResponse(BaseModel):
    """Response body returned for a user resource."""
    id: int
    name: str
    email: str

    model_config = {"from_attributes": True}


class ItemCreate(BaseModel):
    """Request body for creating a new item."""
    title: str
    description: Optional[str] = None
    price: float
    owner_id: int


class ItemResponse(BaseModel):
    """Response body returned for an item resource."""
    id: int
    title: str
    description: Optional[str]
    price: float
    owner_id: int

    model_config = {"from_attributes": True}
