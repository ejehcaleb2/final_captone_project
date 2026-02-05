from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.models.enrollment import Enrollment
from app.schemas.enrollment import EnrollmentCreate, EnrollmentOut
from app.crud.enrollment import enroll_student
from app.deps import get_db, get_current_user

router = APIRouter(prefix="/enrollments", tags=["Enrollments"])


@router.post("/", response_model=EnrollmentOut)
def student_enroll(enrollment: EnrollmentCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # Admins can enroll any student, students can only enroll themselves
    if current_user.role == "admin":
        user_id = enrollment.user_id or current_user.id
    else:
        user_id = current_user.id
        if enrollment.user_id and enrollment.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot enroll another user")
    
    try:
        new_enrollment = enroll_student(db, user_id, enrollment.course_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return new_enrollment


@router.delete("/{course_id}", response_model=dict)
def student_deregister(course_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    enrollment = db.query(Enrollment).filter(
        Enrollment.user_id == current_user.id,
        Enrollment.course_id == course_id
    ).first()

    if not enrollment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")

    db.delete(enrollment)
    db.commit()
    return {"message": "Successfully deregistered from course"}

from app.deps import get_current_admin, get_current_user  # make sure you have this in deps

@router.get("/all", response_model=List[EnrollmentOut])
def view_all_enrollments(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # Admins see all enrollments; students see only their own
    if current_user.role == "admin":
        enrollments = db.query(Enrollment).all()
    else:
        enrollments = db.query(Enrollment).filter(Enrollment.user_id == current_user.id).all()
    return enrollments


@router.get("/course/{course_id}", response_model=List[EnrollmentOut])
def view_course_enrollments(course_id: int, db: Session = Depends(get_db), current_admin = Depends(get_current_admin)):
    enrollments = db.query(Enrollment).filter(Enrollment.course_id == course_id).all()
    return enrollments


@router.delete("/admin/{course_id}/user/{user_id}", response_model=dict)
def admin_remove_student(course_id: int, user_id: int, db: Session = Depends(get_db), current_admin = Depends(get_current_admin)):
    enrollment = db.query(Enrollment).filter(
        Enrollment.course_id == course_id,
        Enrollment.user_id == user_id
    ).first()

    if not enrollment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")

    db.delete(enrollment)
    db.commit()
    return {"message": "Student removed from course successfully"}

from pydantic import BaseModel
from typing import List

class BulkDeregisterRequest(BaseModel):
    user_ids: List[int]

@router.delete("/admin/{course_id}", response_model=dict)
def admin_bulk_remove_students(course_id: int, request: BulkDeregisterRequest, db: Session = Depends(get_db), current_admin = Depends(get_current_admin)):
    removed_count = 0
    for user_id in request.user_ids:
        enrollment = db.query(Enrollment).filter(
            Enrollment.course_id == course_id,
            Enrollment.user_id == user_id
        ).first()
        if enrollment:
            db.delete(enrollment)
            removed_count += 1
    
    if removed_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No enrollments found for the specified users")
    
    db.commit()
    return {"message": f"Removed {removed_count} student(s) from course successfully"}
