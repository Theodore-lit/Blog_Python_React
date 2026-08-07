"""
Schémas Pydantic de sortie pour les endpoints d'authentification.

Règle absolue :
  - hashed_password n'apparaît dans AUCUN de ces schémas.
  - Seuls les champs nécessaires au frontend sont exposés.
"""

from datetime import datetime

from pydantic import BaseModel


class UserResource(BaseModel):
    """Shape d'un utilisateur renvoyé par l'API — sans aucun champ sensible."""

    id: int
    username: str
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResource(BaseModel):
    """Réponse de login : token d'accès + type."""

    access_token: str
    token_type: str = "bearer"


class RegisterResource(BaseModel):
    """Réponse de register : confirmation + données utilisateur publiques."""

    message: str
    user: UserResource
