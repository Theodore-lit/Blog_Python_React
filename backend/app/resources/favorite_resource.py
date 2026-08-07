"""
Schémas Pydantic de sortie pour les endpoints Favorite.
"""

from datetime import datetime

from pydantic import BaseModel

from app.resources.post_resource import PostSummaryResource


class FavoriteResource(BaseModel):
    """Retourné après création d'un favori."""
    id: int
    user_id: int
    post_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class FavoriteToggleResource(BaseModel):
    """Réponse du toggle favori : état courant."""
    favorited: bool   # True = favori créé, False = favori retiré


class FavoriteListResource(BaseModel):
    """Réponse de GET /api/me/favorites — liste des posts favoris de l'utilisateur."""
    total: int
    skip: int
    limit: int
    items: list[PostSummaryResource]
