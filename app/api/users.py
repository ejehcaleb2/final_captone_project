from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app.models.user import User, Base
from app.models.enrollment import Enrollment
from app.core.database import engine
from app.core.security import hash_password, verify_password, create_access_token
from app.deps import get_db
import logging
import sqlalchemy

router = APIRouter()


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str 

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    is_active: bool

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/register", response_model=UserOut)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    
    if user.role not in ("student", "admin"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role")

    
    try:
        existing_user = db.query(User).filter(User.email == user.email).first()
    except (sqlalchemy.exc.ProgrammingError, sqlalchemy.exc.OperationalError) as e:
        logging.exception("Database error during register_user")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="Database error. Ensure migrations have been applied.")

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

  
    hashed_pwd = hash_password(user.password)

    
    new_user = User(
        name=user.name,
        email=user.email,
        hashed_password=hashed_pwd,
        role=user.role,
        is_active=True
    )

   
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except (sqlalchemy.exc.ProgrammingError, sqlalchemy.exc.OperationalError) as e:
        db.rollback()
        logging.exception("Database error when creating user")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="Database error. Ensure migrations have been applied.")

    return new_user


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
   
    try:
        user = db.query(User).filter(User.email == form_data.username).first()
    except (sqlalchemy.exc.ProgrammingError, sqlalchemy.exc.OperationalError) as e:
        logging.exception("Database error during login")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="Database error. Ensure migrations have been applied.")
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email or password"
        )
    # Create JWT token
    access_token = create_access_token(data={"sub": user.email})

    return {"access_token": access_token, "token_type": "bearer"}


class LoginRequest(BaseModel):
    """JSON-based login request (alternative to form-encoded)."""
    email: EmailStr
    password: str


@router.post("/login-json", response_model=Token)
def login_json(creds: LoginRequest, db: Session = Depends(get_db)):
    """JSON-based login endpoint. Use this if sending JSON instead of form data."""
    try:
        user = db.query(User).filter(User.email == creds.email).first()
    except (sqlalchemy.exc.ProgrammingError, sqlalchemy.exc.OperationalError) as e:
        logging.exception("Database error during login_json")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="Database error. Ensure migrations have been applied.")

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    if not verify_password(creds.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint — verifies DB connectivity and tables exist."""
    try:
        # Try to query a count of users (verifies schema exists)
        user_count = db.query(User).count()
        return {
            "status": "healthy",
            "database": "connected",
            "users_table_exists": True,
            "user_count": user_count
        }
    except (sqlalchemy.exc.ProgrammingError, sqlalchemy.exc.OperationalError) as e:
        logging.exception("Database error in health check")
        return {
            "status": "unhealthy",
            "database": "error",
            "detail": str(e),
            "message": "Database error. Ensure migrations have been applied."
        }


from app.deps import get_current_user

@router.get("/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user

from app.deps import get_current_admin

@router.get("/admin-test")
def admin_only_test(admin_user: User = Depends(get_current_admin)):
    return {
        "message": "You are an admin",
        "email": admin_user.email
    }

@router.get("/students", response_model=list[UserOut])
def get_all_students(db: Session = Depends(get_db), admin_user: User = Depends(get_current_admin)):
    students = db.query(User).filter(User.role == "student").all()
    return students

@router.delete("/{user_id}")
def admin_delete_user(user_id: int, db: Session = Depends(get_db), admin_user: User = Depends(get_current_admin)):
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
