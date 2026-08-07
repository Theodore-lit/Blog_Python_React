"""
FavoriteActions — logique métier pour la ressource Favorite.

Flux toggle :
  Route → FavoriteActions → [FavoritePolicy si suppression] → FavoriteRepository → PostgreSQL
                          → audit_service (après l'opération)

Logique toggle (même pattern que LikeActions) :
  - Si le favori n'existe pas  → on le crée   (audit CREATE)
  - Si le favori existe déjà   → on le retire  (audit DELETE)

Règle non négociable :
  La vérification de policy (can_delete_favorite) est appelée EN PREMIÈRE LIGNE
  du bloc de suppression, avant tout appel Repository.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.actions.post_actions import get_post_or_404
from app.models.post import Post
from app.models.user import User
from app.policies.favorite_policy import can_delete_favorite
from app.repositories.favorite_repository import FavoriteRepository
from services.audit_service import ACTION_CREATE, ACTION_DELETE, log_action


def toggle_favorite(
    db: Session,
    current_user: User,
    post_id: int,
    ip_address: str | None = None,
) -> bool:
    """
    Crée le favori s'il n'existe pas, le supprime s'il existe.
    Retourne favorited: bool.
    """
    get_post_or_404(db, post_id)  # lève 404 si le post n'existe pas

    repo = FavoriteRepository(db)
    existing = repo.get_by_user_and_post(user_id=current_user.id, post_id=post_id)

    if existing is None:
        # --- Création du favori ---
        favorite = repo.create(user_id=current_user.id, post_id=post_id)
        log_action(
            db=db,
            action=ACTION_CREATE,
            resource_type="favorite",
            resource_id=favorite.id,
            user_id=current_user.id,
            ip_address=ip_address,
        )
        return True
    else:
        # --- Suppression du favori ---
        # Vérification policy EN PREMIÈRE LIGNE du bloc suppression
        if not can_delete_favorite(current_user, existing):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vous ne pouvez pas retirer le favori d'un autre utilisateur.",
            )
        favorite_id = existing.id
        log_action(
            db=db,
            action=ACTION_DELETE,
            resource_type="favorite",
            resource_id=favorite_id,
            user_id=current_user.id,
            ip_address=ip_address,
        )
        repo.delete(existing)
        return False


def list_user_favorites(
    db: Session,
    current_user: User,
    skip: int = 0,
    limit: int = 20,
) -> tuple[int, list[Post]]:
    """
    Retourne (total, posts) pour la liste des favoris de l'utilisateur connecté.
    Seul l'utilisateur peut consulter SES propres favoris (route protégée par JWT).
    """
    repo = FavoriteRepository(db)
    total = repo.count_by_user(current_user.id)
    posts = repo.list_posts_by_user(current_user.id, skip=skip, limit=limit)
    return total, posts
