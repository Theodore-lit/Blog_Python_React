"""
PostRepository — accès exclusif au modèle Post en base.

Toutes les requêtes SQLAlchemy concernant Post sont écrites ICI.
Ni les Actions ni les Routes ne doivent écrire db.query(Post) directement.
"""

from sqlalchemy.orm import Session

from app.models.post import Post


class PostRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # Lectures
    # ------------------------------------------------------------------

    def get_by_id(self, post_id: int) -> Post | None:
        return self.db.query(Post).filter(Post.id == post_id).first()

    def list_all(self, skip: int = 0, limit: int = 20) -> list[Post]:
        """Liste paginée de tous les posts, du plus récent au plus ancien."""
        return (
            self.db.query(Post)
            .order_by(Post.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def list_by_author(self, author_id: int, skip: int = 0, limit: int = 20) -> list[Post]:
        """Liste paginée des posts d'un auteur donné."""
        return (
            self.db.query(Post)
            .filter(Post.author_id == author_id)
            .order_by(Post.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_all(self) -> int:
        return self.db.query(Post).count()

    def count_by_author(self, author_id: int) -> int:
        return self.db.query(Post).filter(Post.author_id == author_id).count()

    # ------------------------------------------------------------------
    # Écritures
    # ------------------------------------------------------------------

    def create(self, title: str, content: str, author_id: int) -> Post:
        post = Post(title=title, content=content, author_id=author_id)
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)
        return post

    def update(self, post: Post, title: str | None, content: str | None) -> Post:
        if title is not None:
            post.title = title
        if content is not None:
            post.content = content
        self.db.commit()
        self.db.refresh(post)
        return post

    def delete(self, post: Post) -> None:
        self.db.delete(post)
        self.db.commit()
