"""
AuditLog — modèle de journalisation des actions utilisateur.

Règles de sécurité :
  - Ne jamais stocker : mot de passe (haché ou non), token JWT, clé API.
  - Stocker uniquement les MÉTADONNÉES de l'action (qui, quoi, sur quelle ressource, quand, d'où).
  - resource_id est stocké en String pour couvrir les UUIDs futurs sans migration cassante.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.config.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    # Qui — nullable pour les actions anonymes (ex: tentative de login avec email inexistant)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    # Quoi — verbes normalisés : CREATE | READ | UPDATE | DELETE | LOGIN
    action = Column(String(20), nullable=False, index=True)

    # Sur quelle ressource
    resource_type = Column(String(50), nullable=False)   # "post", "comment", "like", "favorite", "user"
    resource_id = Column(String(50), nullable=True)       # id de la ressource affectée

    # Métadonnées réseau — ip_address peut être None si non transmis (batch, CLI, etc.)
    ip_address = Column(String(45), nullable=True)        # 45 chars couvre IPv6 complet

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
