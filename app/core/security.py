from datetime import datetime, timedelta, timezone

from pwdlib import PasswordHash
import jwt

from app.core.config import settings


# Password hashing
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    return password_hash.verify(
        plain_password,
        hashed_password
    )


# JWT token generation
def create_access_token(data: dict):

    # Copy the data so original dictionary isn't modified
    to_encode = data.copy()

    # Token expiration time
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    # Add expiration to token payload
    to_encode.update({"exp": expire})

    # Generate JWT
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt