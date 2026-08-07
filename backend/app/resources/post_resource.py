"""
Schémas Pydantic de sortie pour les endpoints Post.
Seuls les champs nécessaires au frontend sont exposés.
"""

from datetime import datetime

from pydantic import BaseModel


class AuthorSummary(BaseModel):
    """Résumé de l'auteur embarqué dans la réponse Post — sans données sensibles."""
    id: int
    username: str

    model_config = {"from_attributes": True}


class PostResource(BaseModel):
    """Shape d'un post individuel."""
    id: int
    title: str
    content: str
    author_id: int
    author: AuthorSummary
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PostSummaryResource(BaseModel):
    """Shape allégée pour les listes de posts (pas le contenu complet)."""
    id: int
    title: str
    author_id: int
    author: AuthorSummary
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PostListResource(BaseModel):
    """Réponse paginée pour GET /api/posts."""
    total: int
    skip: int
    limit: int
    items: list[PostSummaryResource]
