from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from os import getenv

# Read DATABASE_URL from environment (app.__init__ loads .env in development)
DATABASE_URL = getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is not set. On Render: add your managed Postgres URL to the service's Environment > Environment " \
        "Variables as DATABASE_URL (example: postgresql://user:pass@host:5432/dbname?sslmode=require). Do not commit a .env file to the repo."
    )

# >>>>> CRITICAL FIX: Replace 'postgres://' with 'postgresql://' for SQLAlchemy compatibility
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
# <<<<< END CRITICAL FIX

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
