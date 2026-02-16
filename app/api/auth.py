from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
import logging
import sqlalchemy

from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token
from app.deps import get_db

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


class SignupRequest(BaseModel):
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


@router.post("/signup", response_model=UserOut)
def signup(user: SignupRequest, db: Session = Depends(get_db)):
    """Sign up a new user."""
    if user.role not in ("student", "admin"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role")

    try:
        existing_user = db.query(User).filter(User.email == user.email).first()
    except (sqlalchemy.exc.ProgrammingError, sqlalchemy.exc.OperationalError) as e:
        logging.exception("Database error during signup")
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
    """Log in a user using form-encoded credentials."""
    try:
        user = db.query(User).filter(User.email == form_data.username).first()
    except (sqlalchemy.exc.ProgrammingError, sqlalchemy.exc.OperationalError) as e:
        logging.exception("Database error during login")
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

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


class LoginRequest(BaseModel):
    """JSON-based login request (alternative to form-encoded)."""
    email: EmailStr
    password: str


@router.post("/login-json", response_model=Token)
def login_json(creds: LoginRequest, db: Session = Depends(get_db)):
    """Log in using JSON credentials (alternative to form-encoded)."""
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
