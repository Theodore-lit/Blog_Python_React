"""
LikePolicy — règles d'autorisation pour la ressource Like.

Un like appartient à son créateur : seul lui peut le retirer.
La logique toggle (créer/supprimer) est gérée dans LikeActions ;
la policy garantit qu'on ne peut pas retirer le like d'autrui.
"""

from app.models.like import Like
from app.models.user import User


def can_delete_like(user: User, like: Like) -> bool:
    """Seul l'utilisateur qui a liké peut retirer son like."""
    return like.user_id == user.id
