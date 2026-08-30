"""
OAuth2 password-bearer auth with JWT access tokens and role-based access
control (RBAC). Three roles are modelled, mirroring real investigative units:

  - VIEWER      read-only search / graph / GIS access
  - INVESTIGATOR   VIEWER + ingestion + entity resolution actions
  - ADMIN          INVESTIGATOR + dossier export + user management

This uses an in-memory demo user store (see DEMO_USERS below) so the API is
runnable out of the box. Swap `authenticate_user` / `get_user` for real
Postgres/LDAP-backed lookups in production, and set SECRET_KEY via env var.
"""
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app.core.config import get_settings

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/token")


class Role(str, Enum):
    VIEWER = "viewer"
    INVESTIGATOR = "investigator"
    ADMIN = "admin"


ROLE_RANK = {Role.VIEWER: 0, Role.INVESTIGATOR: 1, Role.ADMIN: 2}


class User(BaseModel):
    username: str
    full_name: str
    role: Role
    disabled: bool = False


class UserInDB(User):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Demo directory — replace with a real user store.
DEMO_USERS: dict[str, UserInDB] = {
    "insp.sharma": UserInDB(
        username="insp.sharma",
        full_name="Inspector R. Sharma",
        role=Role.INVESTIGATOR,
        disabled=False,
        hashed_password=pwd_context.hash("changeme123"),
    ),
    "admin": UserInDB(
        username="admin",
        full_name="System Administrator",
        role=Role.ADMIN,
        disabled=False,
        hashed_password=pwd_context.hash("changeme123"),
    ),
}


def get_user(username: str) -> Optional[UserInDB]:
    return DEMO_USERS.get(username)


def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    user = get_user(username)
    if not user or not pwd_context.verify(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user(username)
    if user is None:
        raise credentials_exception
    return User(**user.model_dump(exclude={"hashed_password"}))


def require_role(minimum: Role):
    """FastAPI dependency factory: require_role(Role.ADMIN) etc."""

    async def _check(user: User = Depends(get_current_user)) -> User:
        if user.disabled:
            raise HTTPException(status_code=403, detail="User account disabled")
        if ROLE_RANK[user.role] < ROLE_RANK[minimum]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires role '{minimum.value}' or higher",
            )
        return user

    return _check
