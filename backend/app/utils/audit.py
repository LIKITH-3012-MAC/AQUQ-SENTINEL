from sqlalchemy.orm import Session
from .. import models
from typing import Any, Dict, Optional

def log_action(
    db: Session,
    action: str,
    user_id: Optional[Any] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
):
    """
    Unified audit logging utility.
    """
    try:
        log_entry = models.AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            action_metadata=metadata
        )
        db.add(log_entry)
        db.commit()
    except Exception as e:
        print(f"[ERROR] Failed to write audit log: {str(e)}")
        db.rollback()
