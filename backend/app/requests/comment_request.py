"""
Schémas Pydantic de validation pour les endpoints Comment.
"""

from pydantic import BaseModel, field_validator


class CreateCommentRequest(BaseModel):
    content: str

    @field_validator("content")
    @classmethod
    def content_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Le contenu du commentaire ne peut pas être vide.")
        return v


class UpdateCommentRequest(BaseModel):
    content: str

    @field_validator("content")
    @classmethod
    def content_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Le contenu du commentaire ne peut pas être vide.")
        return v
