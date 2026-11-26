
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import create_user
from app.core.dependencies import get_current_user, require_role
from app.models.user import User

# Create router instance
router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# User registration API
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):

    try:
        # Call service layer to create user
        new_user = create_user(db, user_data)

        return new_user

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )

@router.get("/me", response_model=UserResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user

@router.get("/admin-test")
def admin_test(
    current_user: User = Depends(require_role("admin"))
):
    return {
        "message": "Welcome Admin!",
        "user": current_user.name,
        "role": current_user.role
    }