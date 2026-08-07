"""
PostActions — logique métier pour la ressource Post.

Flux :
  Route → PostActions → [PostPolicy] → PostRepository → PostgreSQL
                      → audit_service (après l'opération)

Règle non négociable :
  Toute Action qui MODIFIE un post vérifie la Policy EN PREMIÈRE LIGNE,
  avant tout accès Repository.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.post import Post
from app.models.user import User
from app.policies.post_policy import can_delete_post, can_update_post
from app.repositories.post_repository import PostRepository
from services.audit_service import (
    ACTION_CREATE,
    ACTION_DELETE,
    ACTION_UPDATE,
    log_action,
)


def get_post_or_404(db: Session, post_id: int) -> Post:
    """Helper partagé — récupère un post ou lève HTTP 404."""
    repo = PostRepository(db)
    post = repo.get_by_id(post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post introuvable.")
    return post


def list_posts(db: Session, skip: int = 0, limit: int = 20) -> tuple[int, list[Post]]:
    """Retourne (total, items) pour la pagination."""
    repo = PostRepository(db)
    return repo.count_all(), repo.list_all(skip=skip, limit=limit)


def get_post(db: Session, post_id: int) -> Post:
    return get_post_or_404(db, post_id)


def create_post(
    db: Session,
    current_user: User,
    title: str,
    content: str,
    ip_address: str | None = None,
) -> Post:
    repo = PostRepository(db)
    post = repo.create(title=title, content=content, author_id=current_user.id)

    log_action(
        db=db,
        action=ACTION_CREATE,
        resource_type="post",
        resource_id=post.id,
        user_id=current_user.id,
        ip_address=ip_address,
    )
    return post


def update_post(
    db: Session,
    current_user: User,
    post_id: int,
    title: str | None,
    content: str | None,
    ip_address: str | None = None,
) -> Post:
    # Vérification policy EN PREMIÈRE LIGNE avant tout accès Repository
    post = get_post_or_404(db, post_id)
    if not can_update_post(current_user, post):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas autorisé à modifier ce post.",
        )

    repo = PostRepository(db)
    post = repo.update(post, title=title, content=content)

    log_action(
        db=db,
        action=ACTION_UPDATE,
        resource_type="post",
        resource_id=post.id,
        user_id=current_user.id,
        ip_address=ip_address,
    )
    return post


def delete_post(
    db: Session,
    current_user: User,
    post_id: int,
    ip_address: str | None = None,
) -> None:
    # Vérification policy EN PREMIÈRE LIGNE avant tout accès Repository
    post = get_post_or_404(db, post_id)
    if not can_delete_post(current_user, post):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas autorisé à supprimer ce post.",
        )

    # Audit avant delete (le post n'existera plus après)
    log_action(
        db=db,
        action=ACTION_DELETE,
        resource_type="post",
        resource_id=post_id,
        user_id=current_user.id,
        ip_address=ip_address,
    )

    repo = PostRepository(db)
    repo.delete(post)
