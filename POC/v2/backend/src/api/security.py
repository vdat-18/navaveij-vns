from dataclasses import dataclass
from typing import Callable

from fastapi import Depends, Header, HTTPException

from shared.settings import settings


@dataclass
class AuthContext:
    user_id: str
    role: str
    scopes: set[str]


def _split_csv(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


def _parse_scopes(raw: str | None) -> set[str]:
    if not raw:
        return set()
    return {item.strip().lower() for item in _split_csv(raw)}


def get_auth_context(
    x_auth_user_id: str | None = Header(default=None, alias="X-Auth-User-Id"),
    x_auth_role: str | None = Header(default=None, alias="X-Auth-Role"),
    x_auth_scopes: str | None = Header(default=None, alias="X-Auth-Scopes"),
) -> AuthContext:
    auth_mode = settings.api_auth_mode.strip().lower()
    if auth_mode == "disabled":
        return AuthContext(
            user_id=settings.api_auth_default_user_id,
            role=settings.api_auth_default_role.strip().lower(),
            scopes=_parse_scopes(settings.api_auth_default_scopes),
        )
    if not x_auth_user_id or not x_auth_role:
        raise HTTPException(status_code=401, detail="Missing authentication context")
    role = x_auth_role.strip().lower()
    scopes = _parse_scopes(x_auth_scopes)
    return AuthContext(user_id=x_auth_user_id.strip(), role=role, scopes=scopes)


def require_access(*, allowed_roles: set[str], required_scopes: set[str]) -> Callable[[AuthContext], AuthContext]:
    def dependency(context: AuthContext = Depends(get_auth_context)) -> AuthContext:
        if context.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Access forbidden for this role")
        if required_scopes and not required_scopes.issubset(context.scopes):
            raise HTTPException(status_code=403, detail="Missing required scope")
        return context

    return dependency


def parse_roles(raw: str) -> set[str]:
    return {item.strip().lower() for item in _split_csv(raw)}
