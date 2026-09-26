"""
app/routes/users.py
-------------------
FastAPI router handling User CRUD operations.

Endpoints:
    POST   /users/          Create a new user
    GET    /users/{user_id} Retrieve a single user by ID
    GET    /users/          List all users
    DELETE /users/{user_id} Delete a user by ID

This module contains two intentional bugs:
    B1 — POST /users/ returns HTTP 200 instead of the correct 201 Created.
    B2 — The UserCreate schema uses a plain str for email instead of
         EmailStr, so any arbitrary string is accepted without validation.
         (B2 is seeded in app/models.py but is exercised through this route.)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import UserORM, UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user record.

    Accepts a JSON body with `name` and `email` fields.
    Returns the persisted user including its generated `id`.

    Known issue: email is not validated (see B2 in app/models.py).
    """
    existing = db.query(UserORM).filter(UserORM.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = UserORM(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Retrieve a single user by their numeric ID."""
    db_user = db.query(UserORM).filter(UserORM.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.get("/", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db)):
    """Return a list of all registered users."""
    return db.query(UserORM).all()


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete a user by ID. Returns 204 No Content on success."""
    db_user = db.query(UserORM).filter(UserORM.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
