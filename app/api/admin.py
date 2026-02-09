from fastapi import APIRouter, Header, HTTPException
import os
import logging

from alembic.config import Config
from alembic import command
from app.core.database import engine
from sqlalchemy import inspect

router = APIRouter()


@router.post("/admin/migrate")
def run_migrations(x_migrate_token: str = Header(None)):
    """Protected endpoint to run alembic migrations. Supply header `x-migrate-token` matching MIGRATE_SECRET."""
    secret = os.getenv("MIGRATE_SECRET")
    if not secret:
        raise HTTPException(status_code=503, detail="MIGRATE_SECRET not configured on server")
    if x_migrate_token != secret:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        cfg = Config("alembic.ini")
        command.upgrade(cfg, "head")
        return {"status": "ok", "message": "Migrations applied successfully"}
    except Exception:
        logging.exception("Failed to run alembic migrations via HTTP endpoint")
        raise HTTPException(status_code=500, detail="Migration failed; check logs")


@router.get("/admin/tables")
def list_tables(x_migrate_token: str = Header(None)):
    """Return list of tables in the configured database. Protected by same MIGRATE_SECRET."""
    secret = os.getenv("MIGRATE_SECRET")
    if not secret:
        raise HTTPException(status_code=503, detail="MIGRATE_SECRET not configured on server")
    if x_migrate_token != secret:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if engine is None:
        raise HTTPException(status_code=503, detail="Database engine not configured")

    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        return {"tables": tables}
    except Exception:
        logging.exception("Failed to list tables")
        raise HTTPException(status_code=500, detail="Failed to list tables; check logs")
