"""
Routes Comment :
  GET    /api/posts/{post_id}/comments
  POST   /api/posts/{post_id}/comments   (auth requise)
  PUT    /api/comments/{id}              (auth + policy : auteur du commentaire)
  DELETE /api/comments/{id}             (auth + policy : auteur du commentaire OU auteur du post)

Conventions :
  - Aucune logique métier dans les routes — tout délégué aux CommentActions.
  - Lecture publique (pas de JWT requis pour GET).
"""

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.actions import comment_actions
from app.config.database import get_db
from app.middlewares.auth_middleware import get_current_user
from app.models.user import User
from app.requests.comment_request import CreateCommentRequest, UpdateCommentRequest
from app.resources.comment_resource import CommentListResource, CommentResource

# Router pour les routes imbriquées sous /api/posts/{post_id}/comments
posts_router = APIRouter(prefix="/api/posts", tags=["Comments"])

# Router pour les routes directes sur /api/comments/{id}
comments_router = APIRouter(prefix="/api/comments", tags=["Comments"])


def _get_client_ip(request: Request) -> str | None:
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else None


@posts_router.get("/{post_id}/comments", response_model=CommentListResource)
def list_comments(
    post_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> CommentListResource:
    total, comments = comment_actions.list_comments(db, post_id=post_id, skip=skip, limit=limit)
    return CommentListResource(
        total=total,
        skip=skip,
        limit=limit,
        items=[CommentResource.model_validate(c) for c in comments],
    )


@posts_router.post("/{post_id}/comments", response_model=CommentResource, status_code=201)
def create_comment(
    post_id: int,
    payload: CreateCommentRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CommentResource:
    comment = comment_actions.create_comment(
        db=db,
        current_user=current_user,
        post_id=post_id,
        content=payload.content,
        ip_address=_get_client_ip(request),
    )
    return CommentResource.model_validate(comment)


@comments_router.put("/{comment_id}", response_model=CommentResource)
def update_comment(
    comment_id: int,
    payload: UpdateCommentRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CommentResource:
    comment = comment_actions.update_comment(
        db=db,
        current_user=current_user,
        comment_id=comment_id,
        content=payload.content,
        ip_address=_get_client_ip(request),
    )
    return CommentResource.model_validate(comment)


@comments_router.delete("/{comment_id}", status_code=204)
def delete_comment(
    comment_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    comment_actions.delete_comment(
        db=db,
        current_user=current_user,
        comment_id=comment_id,
        ip_address=_get_client_ip(request),
    )
