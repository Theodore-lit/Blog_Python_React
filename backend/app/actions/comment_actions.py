"""
CommentActions — logique métier pour la ressource Comment.

Flux :
  Route → CommentActions → [CommentPolicy] → CommentRepository → PostgreSQL
                         → audit_service (après l'opération)

Règle non négociable :
  Toute Action qui MODIFIE un commentaire vérifie la Policy EN PREMIÈRE LIGNE.

Décision produit (rappel, cohérent avec comment_policy.py) :
  - Peuvent supprimer un commentaire : son auteur OU l'auteur du post parent.
  - Peuvent modifier un commentaire : son auteur uniquement.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.actions.post_actions import get_post_or_404
from app.models.comment import Comment
from app.models.user import User
from app.policies.comment_policy import can_delete_comment, can_update_comment
from app.repositories.comment_repository import CommentRepository
from services.audit_service import (
    ACTION_CREATE,
    ACTION_DELETE,
    ACTION_UPDATE,
    log_action,
)


def _get_comment_or_404(db: Session, comment_id: int) -> Comment:
    repo = CommentRepository(db)
    comment = repo.get_by_id(comment_id)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Commentaire introuvable.")
    return comment


def list_comments(
    db: Session, post_id: int, skip: int = 0, limit: int = 50
) -> tuple[int, list[Comment]]:
    """Vérifie que le post existe, puis retourne (total, items)."""
    get_post_or_404(db, post_id)  # lève 404 si le post n'existe pas
    repo = CommentRepository(db)
    return repo.count_by_post(post_id), repo.list_by_post(post_id, skip=skip, limit=limit)


def create_comment(
    db: Session,
    current_user: User,
    post_id: int,
    content: str,
    ip_address: str | None = None,
) -> Comment:
    get_post_or_404(db, post_id)  # lève 404 si le post n'existe pas

    repo = CommentRepository(db)
    comment = repo.create(content=content, post_id=post_id, author_id=current_user.id)

    log_action(
        db=db,
        action=ACTION_CREATE,
        resource_type="comment",
        resource_id=comment.id,
        user_id=current_user.id,
        ip_address=ip_address,
    )
    return comment


def update_comment(
    db: Session,
    current_user: User,
    comment_id: int,
    content: str,
    ip_address: str | None = None,
) -> Comment:
    # Vérification policy EN PREMIÈRE LIGNE
    comment = _get_comment_or_404(db, comment_id)
    if not can_update_comment(current_user, comment):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas autorisé à modifier ce commentaire.",
        )

    repo = CommentRepository(db)
    comment = repo.update(comment, content=content)

    log_action(
        db=db,
        action=ACTION_UPDATE,
        resource_type="comment",
        resource_id=comment.id,
        user_id=current_user.id,
        ip_address=ip_address,
    )
    return comment


def delete_comment(
    db: Session,
    current_user: User,
    comment_id: int,
    ip_address: str | None = None,
) -> None:
    # Vérification policy EN PREMIÈRE LIGNE
    comment = _get_comment_or_404(db, comment_id)
    post = get_post_or_404(db, comment.post_id)

    if not can_delete_comment(current_user, comment, post):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas autorisé à supprimer ce commentaire.",
        )

    # Audit avant delete
    log_action(
        db=db,
        action=ACTION_DELETE,
        resource_type="comment",
        resource_id=comment_id,
        user_id=current_user.id,
        ip_address=ip_address,
    )

    repo = CommentRepository(db)
    repo.delete(comment)
