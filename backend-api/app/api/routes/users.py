from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app.api.deps import get_db
from app.core.security import get_current_user, hash_password, verify_password
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate, UserPasswordChange, UserResponse
from app.services.auth_service import create_user

router = APIRouter()


def _require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Dependency : l'utilisateur courant doit être admin."""
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Action réservée aux administrateurs",
        )
    return current_user


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Retourne le profil de l'utilisateur connecté."""
    return current_user


@router.put("/me/password")
def change_my_password(
    password_data: UserPasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Changer son propre mot de passe."""
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mot de passe actuel incorrect",
        )
    if len(password_data.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le nouveau mot de passe doit contenir au moins 6 caractères",
        )
    # Fetch fresh user from DB (get_current_user uses its own session)
    db_user = db.query(User).filter(User.id == current_user.id).first()
    db_user.hashed_password = hash_password(password_data.new_password)
    db.add(db_user)
    db.commit()
    return {"message": "Mot de passe mis à jour avec succès"}


@router.get("/", response_model=List[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    _admin: User = Depends(_require_admin),
):
    """Liste tous les utilisateurs (admin uniquement)."""
    return db.query(User).order_by(User.created_at).all()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_new_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(_require_admin),
):
    """Créer un nouvel utilisateur (admin uniquement)."""
    valid_roles = {"admin", "operator", "viewer"}
    if user_data.role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Rôle invalide. Valeurs acceptées : {', '.join(valid_roles)}",
        )
    return create_user(
        db,
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name,
        role=user_data.role,
    )


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(_require_admin),
):
    """Modifier un utilisateur (admin uniquement)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur introuvable",
        )

    # Empêcher la désactivation du dernier administrateur actif
    if user_data.is_active is False and user.role == UserRole.admin:
        admin_count = db.query(User).filter(
            User.role == UserRole.admin,
            User.is_active == True,
            User.id != user_id,
        ).count()
        if admin_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Impossible de désactiver le dernier administrateur actif",
            )

    if user_data.full_name is not None:
        user.full_name = user_data.full_name
    if user_data.role is not None:
        valid_roles = {"admin", "operator", "viewer"}
        if user_data.role not in valid_roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Rôle invalide. Valeurs acceptées : {', '.join(valid_roles)}",
            )
        user.role = UserRole(user_data.role)
    if user_data.is_active is not None:
        user.is_active = user_data.is_active

    db.add(user)
    db.commit()
    db.refresh(user)
    return user
