"""
LikeRepository — accès exclusif au modèle Like en base.
"""

from sqlalchemy.orm import Session

from app.models.like import Like


class LikeRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # Lectures
    # ------------------------------------------------------------------

    def get_by_user_and_post(self, user_id: int, post_id: int) -> Like | None:
        return (
            self.db.query(Like)
            .filter(Like.user_id == user_id, Like.post_id == post_id)
            .first()
        )

    def exists(self, user_id: int, post_id: int) -> bool:
        return self.get_by_user_and_post(user_id, post_id) is not None

    def count_by_post(self, post_id: int) -> int:
        return self.db.query(Like).filter(Like.post_id == post_id).count()

    # ------------------------------------------------------------------
    # Écritures
    # ------------------------------------------------------------------

    def create(self, user_id: int, post_id: int) -> Like:
        like = Like(user_id=user_id, post_id=post_id)
        self.db.add(like)
        self.db.commit()
        self.db.refresh(like)
        return like

    def delete(self, like: Like) -> None:
        self.db.delete(like)
        self.db.commit()
