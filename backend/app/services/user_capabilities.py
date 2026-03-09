"""
User capabilities for unified accounts.

Determines which roles a user can act as:
- job_seeker: always true (anyone can build CV / look for jobs)
- founder: true if user has at least one registered startup
- investor: always true (anyone can invest)
"""
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.db.models import User, Startup


# Role values used in API and frontend (match UserRole values)
JOB_SEEKER_ROLE = "student"
FOUNDER_ROLE = "founder"
INVESTOR_ROLE = "investor"


def get_user_capabilities(db: Session, user: User) -> Dict[str, Any]:
    """
    Compute which roles this user can act as (unified account capabilities).

    Returns:
        {
            "job_seeker": True,
            "founder": bool,  # True if user has at least one startup
            "investor": True,
            "allowed_roles": ["student", "founder", "investor"],  # roles they can switch to
            "primary_role": "student"  # user.role value
        }
    """
    has_startup = (
        db.query(Startup.id).filter(Startup.founder_id == user.id).limit(1).first()
        is not None
    )
    primary = user.role.value if hasattr(user.role, "value") else str(user.role)
    allowed = [JOB_SEEKER_ROLE, INVESTOR_ROLE]
    if has_startup:
        allowed.append(FOUNDER_ROLE)
    # Dedupe and keep order
    allowed = list(dict.fromkeys(allowed))
    return {
        "job_seeker": True,
        "founder": has_startup,
        "investor": True,
        "allowed_roles": allowed,
        "primary_role": primary,
    }


def user_has_capability(db: Session, user: User, role: str) -> bool:
    """Check if user can act as the given role."""
    caps = get_user_capabilities(db, user)
    return role in caps.get("allowed_roles", [])
