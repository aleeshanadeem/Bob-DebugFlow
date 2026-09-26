"""
app/main.py
-----------
Application factory for the Bob DebugFlow sample FastAPI app.

Creates the FastAPI application instance, registers all routers,
and initialises the SQLite database schema on startup.

To run locally:
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI

from app.database import engine, Base
from app.routes import users, items

# Create all ORM-defined tables in the database on startup.
# For the running app this targets debugflow.db (SQLite file).
# For tests, the conftest fixture overrides the engine before this runs.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Bob DebugFlow Sample API",
    description=(
        "A small REST API used as the subject of the Bob DebugFlow "
        "debugging workflow demonstration. Contains intentional bugs."
    ),
    version="1.0.0",
)

app.include_router(users.router)
app.include_router(items.router)


@app.get("/health", tags=["meta"])
def health_check():
    """Simple liveness probe endpoint."""
    return {"status": "ok"}
