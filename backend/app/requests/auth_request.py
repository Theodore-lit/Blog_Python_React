"""
Schémas Pydantic de validation pour les endpoints d'authentification.
Ces schémas définissent et valident les données entrantes — jamais les sorties.
"""

from pydantic import BaseModel, EmailStr, field_validator


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("username")
    @classmethod
    def username_not_empty(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Le nom d'utilisateur doit contenir au moins 3 caractères.")
        if len(v) > 50:
            raise ValueError("Le nom d'utilisateur ne peut pas dépasser 50 caractères.")
        return v

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Le mot de passe doit contenir au moins 8 caractères.")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
