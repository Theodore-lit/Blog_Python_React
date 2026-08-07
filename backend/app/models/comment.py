"""
Comment — commentaire lié à un post.
Relations :
  - post_id   → posts.id   (CASCADE delete : supprimer un post supprime ses commentaires)
  - author_id → users.id   (CASCADE delete : supprimer un user supprime ses commentaires)
"""

from sqlalchemy import Column, ForeignKey, Integer, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.config.database import Base


class Comment(Base):
    __tablename__ = "comments"

    id         = Column(Integer, primary_key=True, index=True)
    content    = Column(Text, nullable=False)
    post_id    = Column(Integer, ForeignKey("posts.id",  ondelete="CASCADE"), nullable=False, index=True)
    author_id  = Column(Integer, ForeignKey("users.id",  ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    post   = relationship("Post", back_populates="comments")
    author = relationship("User", back_populates="comments")
