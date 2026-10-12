from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from Api.jwt import verify_access_token


bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):

    token = credentials.credentials

    payload = verify_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    user_uuid = payload.get("sub")
    role = payload.get("role")

    if not user_uuid or not role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload.",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    return {
        "user_uuid": user_uuid,
        "role": role
    }