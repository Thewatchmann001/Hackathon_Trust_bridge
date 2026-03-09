from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import User
from app.core.security import decode_access_token
from app.services.user_capabilities import user_has_capability
# UnauthorizedAccess removed - using HTTPException directly

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")


def _effective_role(user: User, payload: dict, db: Session) -> str:
    """Resolve effective role for unified account (active_role if allowed, else primary)."""
    primary = user.role.value if hasattr(user.role, "value") else str(user.role)
    active = payload.get("active_role")
    if not active:
        return primary
    if user_has_capability(db, user, active):
        return active
    return primary


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token.
    
    Unified account: token may contain active_role; effective_role is set on user
    for require_role checks.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    
    # Check if account is locked
    from datetime import datetime
    if user.locked_until and user.locked_until > datetime.utcnow():
        remaining_minutes = int((user.locked_until - datetime.utcnow()).total_seconds() / 60)
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Account is locked. Please try again in {remaining_minutes} minutes."
        )
    
    # Unified account: set effective_role (active_role if allowed, else primary)
    effective = _effective_role(user, payload, db)
    setattr(user, "effective_role", effective)
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user."""
    return current_user


def require_role(allowed_roles: list):
    """
    Dependency factory for role-based access control.
    Uses effective_role (unified account active role) when set.
    """
    async def role_checker(current_user: User = Depends(get_current_user)):
        role = getattr(current_user, "effective_role", None) or (
            current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
        )
        # Normalize founder/startup for comparison
        if role == "startup":
            role = "founder"
        allowed_normalized = [r if r != "startup" else "founder" for r in allowed_roles]
        if role not in allowed_normalized:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {allowed_roles}, your active role: {role}"
            )
        return current_user
    return role_checker


def get_current_user_role(payload: dict = None) -> str:
    """
    Extract role from JWT payload.
    
    This is a helper function to get role from token without database lookup.
    Used for logging and audit purposes.
    """
    if payload is None:
        return None
    
    return payload.get("role")

