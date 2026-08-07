from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.config.database import Base


class User(Base):
    __tablename__ = "users"

    id              = Column(Integer, primary_key=True, index=True)
    username        = Column(String(50), unique=True, index=True, nullable=False)
    email           = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at      = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relations — définies ici pour que SQLAlchemy puisse résoudre les back_populates
    posts     = relationship("Post",     back_populates="author",  cascade="all, delete-orphan")
    comments  = relationship("Comment",  back_populates="author",  cascade="all, delete-orphan")
    likes     = relationship("Like",     back_populates="user",    cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="user",    cascade="all, delete-orphan")