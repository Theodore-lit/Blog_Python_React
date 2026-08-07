"""
Routes Favorite :
  POST /api/posts/{post_id}/favorite   — toggle (auth requise)
  GET  /api/me/favorites               — liste des posts favoris (auth requise)

Conventions :
  - La logique toggle est entièrement dans FavoriteActions.
  - /api/me/favorites retourne des PostSummaryResource (pas les favoris bruts),
    ce qui est plus utile pour le frontend React Native.
"""

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.actions import favorite_actions
from app.config.database import get_db
from app.middlewares.auth_middleware import get_current_user
from app.models.user import User
from app.resources.favorite_resource import FavoriteListResource, FavoriteToggleResource
from app.resources.post_resource import PostSummaryResource

# Router pour POST /api/posts/{post_id}/favorite
posts_router = APIRouter(prefix="/api/posts", tags=["Favorites"])

# Router pour GET /api/me/favorites
me_router = APIRouter(prefix="/api/me", tags=["Favorites"])


def _get_client_ip(request: Request) -> str | None:
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else None


@posts_router.post("/{post_id}/favorite", response_model=FavoriteToggleResource)
def toggle_favorite(
    post_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FavoriteToggleResource:
    favorited = favorite_actions.toggle_favorite(
        db=db,
        current_user=current_user,
        post_id=post_id,
        ip_address=_get_client_ip(request),
    )
    return FavoriteToggleResource(favorited=favorited)


@me_router.get("/favorites", response_model=FavoriteListResource)
def list_my_favorites(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FavoriteListResource:
    total, posts = favorite_actions.list_user_favorites(
        db=db,
        current_user=current_user,
        skip=skip,
        limit=limit,
    )
    return FavoriteListResource(
        total=total,
        skip=skip,
        limit=limit,
        items=[PostSummaryResource.model_validate(p) for p in posts],
    )
