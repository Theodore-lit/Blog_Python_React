"""
UserRepository — accès exclusif au modèle User en base.

Convention de ce projet :
  - Les Actions appellent uniquement les méthodes de ce Repository.
  - Aucune requête SQLAlchemy ne doit être écrite en dehors de ce fichier pour le modèle User.
"""

from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # Lectures
    # ------------------------------------------------------------------

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_username(self, username: str) -> User | None:
        return self.db.query(User).filter(User.username == username).first()

    # ------------------------------------------------------------------
    # Écritures
    # ------------------------------------------------------------------

    def create(self, username: str, email: str, hashed_password: str) -> User:
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
