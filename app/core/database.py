from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from os import getenv

# Load database URL from environment variable
DATABASE_URL = getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set. Check your .env file.")

# Configure connect_args for environments that require SSL (e.g., managed Postgres on Render)
connect_args = {}
if DATABASE_URL.startswith("postgresql") and "sslmode=" not in DATABASE_URL:
    connect_args = {"sslmode": "require"}

# Enable pool_pre_ping to avoid using stale/closed connections in pooled environments
engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
