"""
Schémas Pydantic de validation pour les endpoints Post.
"""

from pydantic import BaseModel, field_validator


class CreatePostRequest(BaseModel):
    title: str
    content: str

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Le titre ne peut pas être vide.")
        if len(v) > 255:
            raise ValueError("Le titre ne peut pas dépasser 255 caractères.")
        return v

    @field_validator("content")
    @classmethod
    def content_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Le contenu ne peut pas être vide.")
        return v


class UpdatePostRequest(BaseModel):
    title: str | None = None
    content: str | None = None

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Le titre ne peut pas être vide.")
            if len(v) > 255:
                raise ValueError("Le titre ne peut pas dépasser 255 caractères.")
        return v

    @field_validator("content")
    @classmethod
    def content_not_empty(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Le contenu ne peut pas être vide.")
        return v
