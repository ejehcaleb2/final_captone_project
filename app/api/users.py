from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
import logging
import sqlalchemy

from app.models.user import User
from app.models.enrollment import Enrollment
from app.deps import get_db, get_current_user, get_current_admin

router = APIRouter(prefix="/api/v1/user", tags=["User"])


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    is_active: bool


@router.get("/me", response_model=UserOut)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current authenticated user info."""
    return current_user


@router.get("", response_model=list[UserOut])
def get_all_users(db: Session = Depends(get_db), admin_user: User = Depends(get_current_admin)):
    """Get all users (admin only)."""
    users = db.query(User).all()
    return users


@router.get("/{email}", response_model=UserOut)
def get_user_by_email(email: str, db: Session = Depends(get_db), admin_user: User = Depends(get_current_admin)):
    """Get user by email (admin only)."""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}/activate")
def activate_user(user_id: int, db: Session = Depends(get_db), admin_user: User = Depends(get_current_admin)):
    """Activate a user (admin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = True
    db.commit()
    return {"message": "User activated successfully"}


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), admin_user: User = Depends(get_current_admin)):
    """Delete a user and their enrollments (admin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.role != "student":
        raise HTTPException(status_code=400, detail="Can only delete student accounts")

    # Delete enrollments first
    db.query(Enrollment).filter(Enrollment.user_id == user_id).delete()
    
    # Delete user
    db.delete(user)
    db.commit()
    return {"message": "Student deleted successfully"}
