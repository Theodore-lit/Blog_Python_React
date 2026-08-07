"""
Schémas Pydantic de sortie pour les endpoints Comment.
Seuls les champs nécessaires au frontend sont exposés.
"""

from datetime import datetime

from pydantic import BaseModel


class CommentAuthorSummary(BaseModel):
    id: int
    username: str

    model_config = {"from_attributes": True}


class CommentResource(BaseModel):
    id: int
    content: str
    post_id: int
    author_id: int
    author: CommentAuthorSummary
    created_at: datetime

    model_config = {"from_attributes": True}


class CommentListResource(BaseModel):
    total: int
    skip: int
    limit: int
    items: list[CommentResource]
