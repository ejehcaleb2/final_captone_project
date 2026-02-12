from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from app.models.course import Course
from app.schemas.course import CourseCreate, CourseOut, CourseUpdate
from app.crud.course import create_course, update_course
from app.deps import get_db, get_current_admin, get_current_user
from app.models.user import User

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.post("/", response_model=CourseOut)
def admin_create_course(course: CourseCreate, db: Session = Depends(get_db), admin_user = Depends(get_current_admin)):
    existing_course = db.query(Course).filter(Course.code == course.code).first()
    if existing_course:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course code already exists"
        )

    new_course = create_course(db, course)
    return new_course


@router.get("/", response_model=List[CourseOut])
def get_all_courses(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    courses = db.query(Course).filter(Course.is_active == True).all()
    return courses


@router.get("/{course_id}", response_model=CourseOut)
def get_course(course_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    course = db.query(Course).filter(Course.id == course_id, Course.is_active == True).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.put("/{course_id}", response_model=CourseOut)
def admin_update_course(course_id: int, payload: CourseUpdate, db: Session = Depends(get_db), admin_user = Depends(get_current_admin)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    updated = update_course(db, course, payload)
    return updated

from app.models.enrollment import Enrollment
from app.schemas.user import UserOut

class CourseWithStudentsOut(BaseModel):
    id: int
    title: str
    code: str
    capacity: int
    is_active: bool
    students: list[UserOut]

@router.get("/{course_id}/students", response_model=CourseWithStudentsOut)
def get_course_with_students(course_id: int, db: Session = Depends(get_db), admin_user = Depends(get_current_admin)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    enrollments = db.query(Enrollment).filter(Enrollment.course_id == course_id).all()
    student_ids = [e.user_id for e in enrollments]
    students = db.query(User).filter(User.id.in_(student_ids)).all()
    
    return {
        "id": course.id,
        "title": course.title,
        "code": course.code,
        "capacity": course.capacity,
        "is_active": course.is_active,
        "students": students
    }

@router.delete("/{course_id}")
def admin_delete_course(course_id: int, db: Session = Depends(get_db), admin_user = Depends(get_current_admin)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    enrollments_count = db.query(Enrollment).filter(Enrollment.course_id == course_id).count()
    if enrollments_count > 0:
        raise HTTPException(status_code=400, detail="Cannot delete course with active enrollments")
    
    db.delete(course)
    db.commit()
    return {"message": "Course deleted successfully"}
