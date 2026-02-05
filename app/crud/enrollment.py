from sqlalchemy.orm import Session
from app.models.enrollment import Enrollment
from app.models.course import Course
from app.models.user import User


def enroll_student(db: Session, user_id: int, course_id: int):
    # Check if student is already enrolled in this course
    existing = db.query(Enrollment).filter(
        Enrollment.user_id == user_id,
        Enrollment.course_id == course_id
    ).first()
    if existing:
        raise Exception("Student is already enrolled in this course")

    # Check if course exists and is active
    course = db.query(Course).filter(Course.id == course_id, Course.is_active == True).first()
    if not course:
        raise Exception("Course does not exist or is inactive")

    # Check if course capacity is full
    enrolled_count = db.query(Enrollment).filter(Enrollment.course_id == course_id).count()
    if enrolled_count >= course.capacity:
        raise Exception("Course is full")

    # Create enrollment
    new_enrollment = Enrollment(
        user_id=user_id,
        course_id=course_id
    )
    db.add(new_enrollment)
    db.commit()
    db.refresh(new_enrollment)
    return new_enrollment
