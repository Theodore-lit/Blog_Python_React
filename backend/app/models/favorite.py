"""
Favorite — mise en favori d'un post par un utilisateur.

Contrainte unique (user_id, post_id) : un utilisateur ne peut mettre en favori
un post qu'une seule fois. Même logique que Like.
"""

from sqlalchemy import Column, ForeignKey, Integer, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.config.database import Base


class Favorite(Base):
    __tablename__ = "favorites"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    post_id    = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "post_id", name="uq_favorites_user_post"),
    )

    user = relationship("User", back_populates="favorites")
    post = relationship("Post", back_populates="favorites")
