"""
PostPolicy — règles d'autorisation pour la ressource Post.

Convention :
  Chaque fonction retourne un bool.
  Les Actions vérifient la policy EN PREMIÈRE LIGNE de tout bloc qui modifie une ressource,
  AVANT tout appel Repository.
"""

from app.models.post import Post
from app.models.user import User


def can_update_post(user: User, post: Post) -> bool:
    """Seul l'auteur du post peut le modifier."""
    return post.author_id == user.id


def can_delete_post(user: User, post: Post) -> bool:
    """Seul l'auteur du post peut le supprimer."""
    return post.author_id == user.id
