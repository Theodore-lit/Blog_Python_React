"""
Routes d'authentification : register, login, me.

Conventions :
  - Les routes ne contiennent aucune logique métier.
  - Toute validation d'entrée passe par les schémas Request (Pydantic).
  - Toute mise en forme de sortie passe par les schémas Resource (Pydantic).
  - L'IP est extraite de la Request FastAPI et transmise aux Actions pour l'audit.
  - get_current_user est la seule dependency d'auth utilisée — jamais de vérification
    manuelle de token dans le corps d'une route.
"""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.actions import auth_actions
from app.config.database import get_db
from app.middlewares.auth_middleware import get_current_user
from app.models.user import User
from app.requests.auth_request import LoginRequest, RegisterRequest
from app.resources.auth_resource import RegisterResource, TokenResource, UserResource

router = APIRouter(prefix="/api/auth", tags=["Auth"])


def _get_client_ip(request: Request) -> str | None:
    """Extrait l'IP réelle en tenant compte d'un éventuel reverse proxy."""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else None


@router.post("/register", response_model=RegisterResource, status_code=201)
def register(
    payload: RegisterRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> RegisterResource:
    user = auth_actions.register(
        db=db,
        username=payload.username,
        email=payload.email,
        password=payload.password,
        ip_address=_get_client_ip(request),
    )
    return RegisterResource(
        message="Compte créé avec succès.",
        user=UserResource.model_validate(user),
    )


@router.post("/login", response_model=TokenResource)
def login(
    payload: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> TokenResource:
    token = auth_actions.login(
        db=db,
        email=payload.email,
        password=payload.password,
        ip_address=_get_client_ip(request),
    )
    return TokenResource(access_token=token)


@router.get("/me", response_model=UserResource)
def me(current_user: User = Depends(get_current_user)) -> UserResource:
    """Retourne le profil de l'utilisateur authentifié."""
    return UserResource.model_validate(current_user)
