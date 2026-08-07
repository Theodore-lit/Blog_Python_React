"""
FavoriteRepository — accès exclusif au modèle Favorite en base.
"""

from sqlalchemy.orm import Session

from app.models.favorite import Favorite
from app.models.post import Post


class FavoriteRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # Lectures
    # ------------------------------------------------------------------

    def get_by_user_and_post(self, user_id: int, post_id: int) -> Favorite | None:
        return (
            self.db.query(Favorite)
            .filter(Favorite.user_id == user_id, Favorite.post_id == post_id)
            .first()
        )

    def exists(self, user_id: int, post_id: int) -> bool:
        return self.get_by_user_and_post(user_id, post_id) is not None

    def list_by_user(self, user_id: int, skip: int = 0, limit: int = 20) -> list[Favorite]:
        """Liste des favoris d'un utilisateur, du plus récent au plus ancien."""
        return (
            self.db.query(Favorite)
            .filter(Favorite.user_id == user_id)
            .order_by(Favorite.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_by_user(self, user_id: int) -> int:
        return self.db.query(Favorite).filter(Favorite.user_id == user_id).count()

    def list_posts_by_user(self, user_id: int, skip: int = 0, limit: int = 20) -> list[Post]:
        """Retourne directement les Posts mis en favoris par l'utilisateur (join)."""
        return (
            self.db.query(Post)
            .join(Favorite, Favorite.post_id == Post.id)
            .filter(Favorite.user_id == user_id)
            .order_by(Favorite.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    # ------------------------------------------------------------------
    # Écritures
    # ------------------------------------------------------------------

    def create(self, user_id: int, post_id: int) -> Favorite:
        favorite = Favorite(user_id=user_id, post_id=post_id)
        self.db.add(favorite)
        self.db.commit()
        self.db.refresh(favorite)
        return favorite

    def delete(self, favorite: Favorite) -> None:
        self.db.delete(favorite)
        self.db.commit()
