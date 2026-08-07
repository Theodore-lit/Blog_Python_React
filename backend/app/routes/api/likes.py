"""
Routes Like :
  POST /api/posts/{post_id}/like           — toggle (auth requise)
  GET  /api/posts/{post_id}/likes/count    — compteur public

Conventions :
  - La logique toggle (créer ou supprimer) est entièrement dans LikeActions.
  - La route ne contient aucune condition if/else sur l'état du like.
"""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.actions import like_actions
from app.config.database import get_db
from app.middlewares.auth_middleware import get_current_user
from app.models.user import User
from app.resources.like_resource import LikeCountResource, LikeToggleResource

router = APIRouter(prefix="/api/posts", tags=["Likes"])


def _get_client_ip(request: Request) -> str | None:
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else None


@router.post("/{post_id}/like", response_model=LikeToggleResource)
def toggle_like(
    post_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LikeToggleResource:
    liked, likes_count = like_actions.toggle_like(
        db=db,
        current_user=current_user,
        post_id=post_id,
        ip_address=_get_client_ip(request),
    )
    return LikeToggleResource(liked=liked, likes_count=likes_count)


@router.get("/{post_id}/likes/count", response_model=LikeCountResource)
def get_likes_count(
    post_id: int,
    db: Session = Depends(get_db),
) -> LikeCountResource:
    count = like_actions.get_likes_count(db, post_id)
    return LikeCountResource(post_id=post_id, likes_count=count)
