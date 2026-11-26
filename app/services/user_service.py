from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import hash_password


# Get a user using their ID
def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


# Get a user using their email
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


# Get all users
def get_all_users(db: Session):
    return db.query(User).all()


# Create a new user
def create_user(db: Session, user_data: UserCreate):

    # Check whether email already exists
    existing_user = get_user_by_email(db, user_data.email)

    if existing_user:
        raise ValueError("Email already registered")

    # Convert Pydantic data into a dictionary
    user_dict = user_data.model_dump()

    # Hash password before saving
    user_dict["hashed_password"] = hash_password(user_dict.pop("password"))

    # Create SQLAlchemy User object
    new_user = User(**user_dict)

    # Save user to database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# Update an existing user
def update_user(db: Session, user_id: int, user_data: UserUpdate):

    user = get_user_by_id(db, user_id)

    if not user:
        return None

    # Get only fields supplied by the client
    update_data = user_data.model_dump(exclude_unset=True)

    # Handle password separately
    password = update_data.pop("password", None)

    if password is not None:
        update_data["hashed_password"] = hash_password(password)

    # Check for duplicate email
    new_email = update_data.get("email")

    if new_email and new_email != user.email:
        existing_user = get_user_by_email(db, new_email)

        if existing_user:
            raise ValueError("Email already registered")

    # Update user fields
    for key, value in update_data.items():
        if value is not None:
            setattr(user, key, value)

    db.commit()
    db.refresh(user)

    return user


# Delete a user
def delete_user(db: Session, user_id: int):

    user = get_user_by_id(db, user_id)

    if not user:
        return None

    db.delete(user)
    db.commit()

    return user