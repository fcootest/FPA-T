"""Auth stub (ISP S2). V1.0 = stub; V1.1 replaces with real JWT/OIDC."""
from dataclasses import dataclass
from fastapi import Header


@dataclass
class UserContext:
    email: str
    role: str  # role claim from token


async def get_current_user(
    x_user_email: str = Header(default="dev@fpa-t.local"),
    x_user_role: str = Header(default="admin"),
) -> UserContext:
    """Stub: read user identity from request headers. Replace with JWT in V1.1."""
    return UserContext(email=x_user_email, role=x_user_role)
