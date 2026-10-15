from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from config import get_settings


settings = get_settings()

SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

REQUIRED_TOKEN_CLAIMS = ["exp", "sub", "role"]


def create_access_token(data: dict) -> str:
    """
    Create a signed JWT access token with a 30-minute expiration.
    """
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def verify_access_token(token: str):
    """
    Verify the JWT signature, expiration, and required claims.

    Returns:
        dict: Decoded token payload when valid.
        None: When the token is invalid or expired.
    """
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={
                "require_exp": True,
                "require_sub": True,
                "require_role": True,
            },
        )

        return payload

    except JWTError:
        return None
