"""
CommentPolicy — règles d'autorisation pour la ressource Comment.

Décision produit (documentée ici) :
  Peuvent supprimer un commentaire :
    1. L'auteur du commentaire lui-même.
    2. L'auteur du post sur lequel le commentaire est posté
       (modération de son propre espace).
  Personne d'autre ne peut supprimer un commentaire via l'API publique.
"""

from app.models.comment import Comment
from app.models.post import Post
from app.models.user import User


def can_delete_comment(user: User, comment: Comment, post: Post) -> bool:
    """Auteur du commentaire OU auteur du post parent peuvent supprimer."""
    return comment.author_id == user.id or post.author_id == user.id


def can_update_comment(user: User, comment: Comment) -> bool:
    """Seul l'auteur peut modifier le contenu de son commentaire."""
    return comment.author_id == user.id
