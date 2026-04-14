from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """Créer un nouvel utilisateur."""
    email: str = Field(..., description="Adresse email")
    password: str = Field(..., min_length=6, description="Mot de passe (min 6 caractères)")
    full_name: str = Field(default="", description="Nom complet")
    role: str = Field(default="viewer", description="Rôle : admin / operator / viewer")


class UserUpdate(BaseModel):
    """Modifier un utilisateur existant."""
    full_name: Optional[str] = Field(None, description="Nom complet")
    role: Optional[str] = Field(None, description="Rôle : admin / operator / viewer")
    is_active: Optional[bool] = Field(None, description="Actif ou non")


class UserPasswordChange(BaseModel):
    """Changer son propre mot de passe."""
    current_password: str = Field(..., description="Mot de passe actuel")
    new_password: str = Field(..., min_length=6, description="Nouveau mot de passe (min 6 caractères)")


class UserResponse(BaseModel):
    """Réponse utilisateur."""
    id: UUID
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
