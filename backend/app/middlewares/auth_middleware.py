"""
auth_middleware.py — Dependency FastAPI pour l'authentification JWT.

Usage dans les routes protégées :
    current_user: User = Depends(get_current_user)

Ce module est le SEUL endroit où le token JWT est décodé.
Aucune route ne doit vérifier un token manuellement dans son corps.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config.settings import settings
from app.models.user import User
from app.repositories.user_repository import UserRepository

# tokenUrl pointe vers l'endpoint de login — utilisé par Swagger UI pour le bouton Authorize
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Token invalide ou expiré.",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Décode le JWT, extrait le user_id (sub), charge l'utilisateur via UserRepository.
    Lève HTTP 401 si le token est invalide, expiré, ou si l'utilisateur n'existe plus.

    Convention de sécurité :
      - On ne logue JAMAIS le contenu du token ici.
      - On ne retourne JAMAIS hashed_password dans cet objet (le modèle SQLAlchemy
        le contient, mais les Resources Pydantic l'excluent systématiquement).
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise CREDENTIALS_EXCEPTION
    except JWTError:
        raise CREDENTIALS_EXCEPTION

    repo = UserRepository(db)
    user = repo.get_by_id(int(user_id))
    if user is None:
        raise CREDENTIALS_EXCEPTION

    return user
