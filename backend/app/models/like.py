"""
Like — like d'un utilisateur sur un post.

Contrainte unique (user_id, post_id) : un utilisateur ne peut liker
un post qu'une seule fois. La tentative de doublon lève une IntegrityError
interceptée dans LikeActions avant d'atteindre la base.
"""

from sqlalchemy import Column, ForeignKey, Integer, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.config.database import Base


class Like(Base):
    __tablename__ = "likes"

    id        = Column(Integer, primary_key=True, index=True)
    user_id   = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    post_id   = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "post_id", name="uq_likes_user_post"),
    )

    user = relationship("User", back_populates="likes")
    post = relationship("Post", back_populates="likes")
