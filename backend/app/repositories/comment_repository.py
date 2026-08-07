"""
CommentRepository — accès exclusif au modèle Comment en base.
"""

from sqlalchemy.orm import Session

from app.models.comment import Comment


class CommentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # Lectures
    # ------------------------------------------------------------------

    def get_by_id(self, comment_id: int) -> Comment | None:
        return self.db.query(Comment).filter(Comment.id == comment_id).first()

    def list_by_post(self, post_id: int, skip: int = 0, limit: int = 50) -> list[Comment]:
        return (
            self.db.query(Comment)
            .filter(Comment.post_id == post_id)
            .order_by(Comment.created_at.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_by_post(self, post_id: int) -> int:
        return self.db.query(Comment).filter(Comment.post_id == post_id).count()

    # ------------------------------------------------------------------
    # Écritures
    # ------------------------------------------------------------------

    def create(self, content: str, post_id: int, author_id: int) -> Comment:
        comment = Comment(content=content, post_id=post_id, author_id=author_id)
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def update(self, comment: Comment, content: str) -> Comment:
        comment.content = content
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def delete(self, comment: Comment) -> None:
        self.db.delete(comment)
        self.db.commit()
