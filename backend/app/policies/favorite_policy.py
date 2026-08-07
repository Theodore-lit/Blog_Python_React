"""
FavoritePolicy — règles d'autorisation pour la ressource Favorite.

Un favori est strictement personnel : seul son créateur peut le retirer.
"""

from app.models.favorite import Favorite
from app.models.user import User


def can_delete_favorite(user: User, favorite: Favorite) -> bool:
    """Seul l'utilisateur qui a mis en favori peut le retirer."""
    return favorite.user_id == user.id
