import json
from sqlalchemy.orm import Session
from . import models


def record_audit(db: Session, entity_type: str, entity_id: str | None, action: str, payload: dict | None = None):
    entry = models.AuditEntry(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        payload=json.dumps(payload) if payload is not None else None,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
