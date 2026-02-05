from sqlalchemy import Column, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.user import User
from app.models.course import Course

class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="enrollments")
    course = relationship("Course", backref="enrollments")
