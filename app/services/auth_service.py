
from typing import cast

from sqlalchemy.orm import Session

from app.models.user import User
from app.core.security import verify_password


def authenticate_user(
    db: Session,
    email: str,
    password: str
):
    # Find user using email
    user = db.query(User).filter(User.email == email).first()

    # Check if user exists
    if not user:
        return None

    # Tell Pylance these database attributes are Python values
    hashed_password = cast(str, user.hashed_password)
    is_active = cast(bool, user.is_active)

    # Verify entered password against stored hash
    if not verify_password(password, hashed_password):
        return None

    # Check whether account is active
    if not is_active:
        return None

    return user
