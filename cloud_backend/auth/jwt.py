from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from cloud_backend.config import settings

ALGORITHM = "HS256"

def create_access_token(data: dict) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(
        {**data, "exp": expire},
        settings.SECRET_KEY,
        algorithm=ALGORITHM
    )

def verify_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None
