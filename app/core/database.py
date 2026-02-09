from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from os import getenv

# Load database URL from environment variable
DATABASE_URL = getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set. Check your .env file.")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
