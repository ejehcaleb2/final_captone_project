from fastapi import FastAPI
from dotenv import load_dotenv
from app.api import enrollment, users, courses, auth, admin
import os
import logging

# Alembic imports for programmatic migrations
from alembic.config import Config
from alembic import command

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Course Enrollment Platform", version="1.0.0")


def run_alembic_migrations():
    """Run Alembic migrations programmatically using alembic.ini at repo root."""
    try:
        cfg = Config("alembic.ini")
        command.upgrade(cfg, "head")
        logging.info("Alembic migrations applied successfully.")
    except Exception:
        logging.exception("Failed to run alembic migrations")


@app.on_event("startup")
def on_startup():
    # Optionally auto-run migrations in deployed environments when enabled
    auto = os.getenv("AUTO_MIGRATE", "false").lower()
    if auto in ("1", "true", "yes"):
        logging.info("AUTO_MIGRATE enabled — running alembic migrations on startup")
        run_alembic_migrations()


# Include routers with /api/v1 structure
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(courses.router)
app.include_router(enrollment.router)
app.include_router(admin.router)


@app.get("/")
def read_root():
    return {"message": "Hello, Course Enrollment API is running!"}
