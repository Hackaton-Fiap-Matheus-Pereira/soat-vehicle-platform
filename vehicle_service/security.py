from dataclasses import dataclass

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import get_settings

bearer = HTTPBearer()


@dataclass
class Principal:
    user_id: str
    role: str


def current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer)) -> Principal:
    settings = get_settings()
    try:
        payload = jwt.decode(credentials.credentials, settings.jwt_secret,
                             algorithms=[settings.jwt_algorithm], issuer="soat-auth-service")
        return Principal(user_id=payload["sub"], role=payload["role"])
    except (jwt.PyJWTError, KeyError) as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from exc


def admin_only(user: Principal = Depends(current_user)) -> Principal:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Administrator access required")
    return user

