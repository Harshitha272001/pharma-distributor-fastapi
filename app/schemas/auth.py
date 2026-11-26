from pydantic import BaseModel, EmailStr


# Data required for login
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# Response after successful login
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"