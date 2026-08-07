"""
LikeActions — logique métier pour la ressource Like.

Flux toggle :
  Route → LikeActions → [LikePolicy si suppression] → LikeRepository → PostgreSQL
                      → audit_service (après l'opération)

Logique toggle (documentée ici, dans l'Action — pas dans la Route) :
  - Si le like n'existe pas  → on le crée   (audit CREATE)
  - Si le like existe déjà   → on le retire  (audit DELETE)
  Le résultat retourné indique l'état courant et le nouveau compteur.

Règle non négociable :
  La vérification de policy (can_delete_like) est appelée EN PREMIÈRE LIGNE
  du bloc de suppression, avant tout appel Repository.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.actions.post_actions import get_post_or_404
from app.models.user import User
from app.policies.like_policy import can_delete_like
from app.repositories.like_repository import LikeRepository
from services.audit_service import ACTION_CREATE, ACTION_DELETE, log_action


def toggle_like(
    db: Session,
    current_user: User,
    post_id: int,
    ip_address: str | None = None,
) -> tuple[bool, int]:
    """
    Crée le like s'il n'existe pas, le supprime s'il existe.
    Retourne (liked: bool, likes_count: int).
    """
    get_post_or_404(db, post_id)  # lève 404 si le post n'existe pas

    repo = LikeRepository(db)
    existing = repo.get_by_user_and_post(user_id=current_user.id, post_id=post_id)

    if existing is None:
        # --- Création du like ---
        like = repo.create(user_id=current_user.id, post_id=post_id)
        log_action(
            db=db,
            action=ACTION_CREATE,
            resource_type="like",
            resource_id=like.id,
            user_id=current_user.id,
            ip_address=ip_address,
        )
        liked = True
    else:
        # --- Suppression du like ---
        # Vérification policy EN PREMIÈRE LIGNE du bloc suppression
        if not can_delete_like(current_user, existing):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vous ne pouvez pas retirer le like d'un autre utilisateur.",
            )
        like_id = existing.id
        log_action(
            db=db,
            action=ACTION_DELETE,
            resource_type="like",
            resource_id=like_id,
            user_id=current_user.id,
            ip_address=ip_address,
        )
        repo.delete(existing)
        liked = False

    likes_count = repo.count_by_post(post_id)
    return liked, likes_count


def get_likes_count(db: Session, post_id: int) -> int:
    """Retourne le nombre de likes d'un post (lecture publique)."""
    get_post_or_404(db, post_id)
    repo = LikeRepository(db)
    return repo.count_by_post(post_id)
