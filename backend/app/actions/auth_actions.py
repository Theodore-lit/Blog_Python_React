"""
AuthActions — logique métier pour l'authentification.

Flux :
  Route → AuthActions → UserRepository → PostgreSQL
                      → audit_service (après l'opération Repository)

Règles de sécurité :
  - Hash exclusivement via passlib + bcrypt.
  - Le mot de passe en clair n'est jamais loggué ni stocké autrement que haché.
  - Le token JWT n'est jamais loggué.
  - Les actions appellent UserRepository — jamais db.query() directement.
"""

from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.models.user import User
from app.repositories.user_repository import UserRepository
from services.audit_service import ACTION_CREATE, ACTION_LOGIN, log_action

# Contexte de hachage — bcrypt uniquement, cohérent avec le choix du projet
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------------------------------------------------------------------------
# Helpers internes
# ---------------------------------------------------------------------------

def _hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def _verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def _create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


# ---------------------------------------------------------------------------
# Actions publiques
# ---------------------------------------------------------------------------

def register(
    db: Session,
    username: str,
    email: str,
    password: str,
    ip_address: str | None = None,
) -> User:
    """
    Crée un nouvel utilisateur.
    Vérifie l'unicité de l'email et du username avant insertion.
    """
    repo = UserRepository(db)

    if repo.get_by_email(email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un compte avec cet email existe déjà.",
        )
    if repo.get_by_username(username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ce nom d'utilisateur est déjà pris.",
        )

    hashed = _hash_password(password)
    user = repo.create(username=username, email=email, hashed_password=hashed)

    # Audit — après création réussie. On logue CREATE sur resource "user".
    # On ne logue PAS le mot de passe ni le hash.
    log_action(
        db=db,
        action=ACTION_CREATE,
        resource_type="user",
        resource_id=user.id,
        user_id=user.id,
        ip_address=ip_address,
    )

    return user


def login(
    db: Session,
    email: str,
    password: str,
    ip_address: str | None = None,
) -> str:
    """
    Authentifie un utilisateur et retourne un token JWT.
    Lève HTTP 401 si les identifiants sont invalides.

    Note : on retourne intentionnellement le même message d'erreur
    qu'email ou mot de passe soient incorrects (pas d'énumération des comptes).
    """
    repo = UserRepository(db)
    user = repo.get_by_email(email)

    INVALID = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Email ou mot de passe incorrect.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if user is None or not _verify_password(password, user.hashed_password):
        raise INVALID

    token = _create_access_token(user.id)

    # Audit — LOGIN sur resource "user". user_id connu car authentification réussie.
    log_action(
        db=db,
        action=ACTION_LOGIN,
        resource_type="user",
        resource_id=user.id,
        user_id=user.id,
        ip_address=ip_address,
    )

    return token
