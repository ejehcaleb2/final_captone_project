from sqlalchemy import Column, Integer, String, Boolean
from app.core.database import Base

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    code = Column(String, unique=True, nullable=False, index=True)
    capacity = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
