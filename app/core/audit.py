from typing import Optional, Dict, Any
from datetime import datetime, timezone
from app.core.db import require_db
from app.core.security import get_role

def audit(request, action: str, entity_type: str, entity_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
    db = require_db()
    request_id = request.state.request_id if hasattr(request.state, "request_id") else "-"
    db.audit_logs.insert_one({
        "ts": datetime.now(timezone.utc).isoformat(),
        "request_id": request_id,
        "actor_role": get_role(request),
        "action": action,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "metadata": metadata or {},
    })
