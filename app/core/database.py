from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from os import getenv

# Load database URL from environment variable
DATABASE_URL = getenv("DATABASE_URL", "postgresql://localhost/course_enrollment_db")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
