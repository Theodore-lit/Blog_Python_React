"""
AuditRepository — écriture des entrées d'audit en base.

Point d'appel unique : les Actions appellent audit_service.log_action()
qui délègue à ce Repository. Ni les Routes ni les autres Repositories
n'écrivent jamais directement dans audit_logs.
"""

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


class AuditRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        user_id: int | None,
        action: str,
        resource_type: str,
        resource_id: str | None,
        ip_address: str | None,
    ) -> AuditLog:
        entry = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id is not None else None,
            ip_address=ip_address,
        )
        self.db.add(entry)
        # On flush sans commit pour que l'audit soit inclus dans la transaction
        # parente si l'appelant gère lui-même le commit (ex: create post + audit atomique).
        # Si le service appelle log_action après un commit Repository, on commit ici.
        self.db.commit()
        self.db.refresh(entry)
        return entry
