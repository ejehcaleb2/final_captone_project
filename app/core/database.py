from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from os import getenv
import sys

# Load database URL from environment variable
DATABASE_URL = getenv("DATABASE_URL")

if not DATABASE_URL:
    print("\n" + "="*70)
    print("ERROR: DATABASE_URL environment variable is not set!")
    print("Please add DATABASE_URL to your .env file with PostgreSQL connection string.")
    print("\nExample: DATABASE_URL=postgresql://user:password@localhost:5432/course_enrollment_db")
    print("\nFor Render: DATABASE_URL=postgresql://user:password@your_render_host:5432/dbname")
    print("="*70 + "\n")
    sys.exit(1)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
