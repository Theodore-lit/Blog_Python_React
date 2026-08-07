"""
AuditService — point d'appel unique pour journaliser toutes les actions.

Convention choisie (documentée ici) :
  Les Actions (app/actions/) appellent log_action() APRÈS l'opération Repository,
  au sein du même flux de la requête HTTP. Cela garantit :
    1. Qu'on ne logue pas une action qui aurait échoué (repository levait une exception).
    2. Que le log porte le resource_id réel retourné par le Repository (ex: id auto-incrémenté).
    3. Un seul point d'entrée, facile à mocker dans les tests.

Données jamais loguées :
  - Mot de passe en clair ou haché
  - Token JWT
  - Clé API ou tout champ chiffré
"""

from sqlalchemy.orm import Session

from app.repositories.audit_repository import AuditRepository


# Verbes normalisés — utiliser ces constantes dans tout le projet
ACTION_CREATE = "CREATE"
ACTION_READ   = "READ"
ACTION_UPDATE = "UPDATE"
ACTION_DELETE = "DELETE"
ACTION_LOGIN  = "LOGIN"


def log_action(
    db: Session,
    action: str,
    resource_type: str,
    resource_id: int | str | None = None,
    user_id: int | None = None,
    ip_address: str | None = None,
) -> None:
    """
    Enregistre une entrée d'audit.

    Paramètres :
        db            — session SQLAlchemy (injectée depuis la route via Depends)
        action        — verbe (ACTION_CREATE, ACTION_LOGIN, …)
        resource_type — nom de la ressource en minuscule ("post", "user", …)
        resource_id   — identifiant de la ressource affectée (None si N/A, ex: login)
        user_id       — id de l'utilisateur qui agit (None si anonyme)
        ip_address    — IP source de la requête (None si non disponible)
    """
    repo = AuditRepository(db)
    repo.create(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        ip_address=ip_address,
    )
