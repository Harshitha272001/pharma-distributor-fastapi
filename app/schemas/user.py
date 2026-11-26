#models/user.py represents the database structure, whereas schemas/user.py represents the data entering and leaving our API.

# Schema for receiving user registration data
from typing import Literal

from pydantic import BaseModel, EmailStr, ConfigDict

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Literal["admin", "staff", "qa", "distributor"] = "distributor"

# Schema for updating user details
class UserUpdate(BaseModel):
    name: str | None = None #(None refers to the fact that this field is optional)
    email: EmailStr | None = None
    password: str | None = None
    role: Literal["admin", "staff", "qa", "distributor"] | None = None

# Schema for returning user details through API
class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    is_active: bool
    role: str

#Since SQLAlchemy returns Python model objects rather than dictionaries,
#Pydantic needs to know how to read their attributes.
    model_config = ConfigDict(from_attributes=True)
