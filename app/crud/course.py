from sqlalchemy.orm import Session
from app.models.course import Course
from app.schemas.course import CourseCreate, CourseUpdate

def create_course(db: Session, course: CourseCreate):
    new_course = Course(
        title=course.title,
        code=course.code,
        capacity=course.capacity,
        is_active=True
    )
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course

def update_course(db: Session, course: Course, payload: CourseUpdate):
    if payload.title is not None:
        course.title = payload.title
    if payload.capacity is not None:
        course.capacity = payload.capacity
    if payload.is_active is not None:
        course.is_active = payload.is_active

    db.add(course)
    db.commit()
    db.refresh(course)
    return course

