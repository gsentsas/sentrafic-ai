from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.auth import LoginRequest, TokenResponse, UserResponse
from app.services.auth_service import authenticate_user, create_access_token_for_user

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(
    login_request: LoginRequest,
    db: Session = Depends(get_db),
):
    """
    Authenticate user and return JWT token.

    - **email**: User email address
    - **password**: User password
    """
    user = authenticate_user(db, login_request.email, login_request.password)
    return create_access_token_for_user(user)


@router.post("/register", response_model=UserResponse)
def register(
    email: str,
    password: str,
    full_name: str = "",
    db: Session = Depends(get_db),
):
    """Register a new user."""
    from app.services.auth_service import create_user

    user = create_user(
        db,
        email=email,
        password=password,
        full_name=full_name,
        role="viewer",
    )
    return UserResponse.from_orm(user)
