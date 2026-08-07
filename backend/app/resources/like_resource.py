"""
Schémas Pydantic de sortie pour les endpoints Like.
"""

from datetime import datetime

from pydantic import BaseModel


class LikeResource(BaseModel):
    """Retourné après un like créé."""
    id: int
    user_id: int
    post_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class LikeToggleResource(BaseModel):
    """Réponse du toggle like : état courant + compteur."""
    liked: bool          # True = like créé, False = like retiré
    likes_count: int


class LikeCountResource(BaseModel):
    """Réponse de GET /api/posts/{post_id}/likes/count."""
    post_id: int
    likes_count: int
