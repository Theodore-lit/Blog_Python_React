"""
Routes Post : GET /api/posts, GET /api/posts/{id},
              POST /api/posts, PUT /api/posts/{id}, DELETE /api/posts/{id}.

Conventions :
  - Lecture publique (pas de JWT requis pour GET).
  - Création/modification/suppression : Depends(get_current_user).
  - Aucune logique métier ici — tout délégué aux PostActions.
"""

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.actions import post_actions
from app.config.database import get_db
from app.middlewares.auth_middleware import get_current_user
from app.models.user import User
from app.requests.post_request import CreatePostRequest, UpdatePostRequest
from app.resources.post_resource import PostListResource, PostResource, PostSummaryResource

router = APIRouter(prefix="/api/posts", tags=["Posts"])


def _get_client_ip(request: Request) -> str | None:
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else None


@router.get("", response_model=PostListResource)
def list_posts(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> PostListResource:
    total, posts = post_actions.list_posts(db, skip=skip, limit=limit)
    return PostListResource(
        total=total,
        skip=skip,
        limit=limit,
        items=[PostSummaryResource.model_validate(p) for p in posts],
    )


@router.get("/{post_id}", response_model=PostResource)
def get_post(
    post_id: int,
    db: Session = Depends(get_db),
) -> PostResource:
    post = post_actions.get_post(db, post_id)
    return PostResource.model_validate(post)


@router.post("", response_model=PostResource, status_code=201)
def create_post(
    payload: CreatePostRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PostResource:
    post = post_actions.create_post(
        db=db,
        current_user=current_user,
        title=payload.title,
        content=payload.content,
        ip_address=_get_client_ip(request),
    )
    return PostResource.model_validate(post)


@router.put("/{post_id}", response_model=PostResource)
def update_post(
    post_id: int,
    payload: UpdatePostRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PostResource:
    post = post_actions.update_post(
        db=db,
        current_user=current_user,
        post_id=post_id,
        title=payload.title,
        content=payload.content,
        ip_address=_get_client_ip(request),
    )
    return PostResource.model_validate(post)


@router.delete("/{post_id}", status_code=204)
def delete_post(
    post_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    post_actions.delete_post(
        db=db,
        current_user=current_user,
        post_id=post_id,
        ip_address=_get_client_ip(request),
    )
