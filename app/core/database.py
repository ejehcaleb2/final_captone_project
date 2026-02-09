from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from os import getenv

# Load database URL from environment variable
DATABASE_URL = getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set. Check your .env file.")

# Configure connect_args for SSL (only for remote connections, not localhost)
connect_args = {}
if DATABASE_URL.startswith("postgresql") and "localhost" not in DATABASE_URL and "127.0.0.1" not in DATABASE_URL:
    # Only require SSL for remote Render connections; localhost should not use SSL
    if "sslmode=" not in DATABASE_URL:
        connect_args = {"sslmode": "require"}

# Enable pool_pre_ping to avoid using stale/closed connections in pooled environments
engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
