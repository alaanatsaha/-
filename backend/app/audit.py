from __future__ import annotations

"""Small audit logging helper kept independent from business rules."""
from typing import Optional

from fastapi import Request
from sqlalchemy.orm import Session

from .models import AuditLog


def record_event(
    db: Session,
    request: Request,
    action: str,
    assessment_id: Optional[int] = None,
    actor: str = "anonymous",
) -> None:
    forwarded_for = request.headers.get("x-forwarded-for", "")
    ip_address = forwarded_for.split(",")[0].strip() or (
        request.client.host if request.client else "unknown"
    )
    db.add(
        AuditLog(
            action=action,
            actor=actor,
            assessment_id=assessment_id,
            ip_address=ip_address,
            user_agent=request.headers.get("user-agent", "")[:512],
        )
    )
    db.commit()