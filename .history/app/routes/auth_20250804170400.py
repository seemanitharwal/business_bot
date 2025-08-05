from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from app.models.user import User, UserCreate, UserLogin, Token
from app.auth.auth_handler import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    get_current_active_user
)
from app.database import get_database
from app.config import settings
from bson import ObjectId
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/register", response_model=User)
async def register(user: UserCreate):
    """Register new user"""
    db = get_database()
    
    # Validate input
    if not user.email or not user.password or not user.full_name:
        raise HTTPException(
            status_code=400,
            detail="Email, password, and full name are required"
        )
    
    if len(user.password) < 6:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 6 characters"
        )
    
    if len(user.full_name.strip()) < 2:
        raise HTTPException(
            status_code=400,
            detail="Full name must be at least 2 characters"
        )
    
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user.email.lower().strip()})
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Count how many users are already in the DB
    existing_users = await db.users.count_documents({})
    
    # Create user dictionary
    user_dict = user.dict()
    user_dict["email"] = user.email.lower().strip()
    user_dict["full_name"] = user.full_name.strip()
    user_dict["hashed_password"] = get_password_hash(user.password)
    # Ensure username is present and unique to avoid DuplicateKeyError on null
    user_dict["username"] = user.email.lower().strip()
    user_dict["created_at"] = datetime.utcnow()
    user_dict["updated_at"] = datetime.utcnow()
    user_dict["workspaces"] = []

    # Set role and is_admin for first user
    if existing_users == 0:
        user_dict["role"] = "admin"
        user_dict["is_admin"] = True
    else:
        user_dict["role"] = "member"a
        user_dict["is_admin"] = False

    # Remove plaintext password
    del user_dict["password"]

    # Insert user into DB
    try:
    result = await db.users.insert_one(user_dict)
    except Exception as e:
        # Handle duplicate username/email errors
        from pymongo.errors import DuplicateKeyError
        if isinstance(e, DuplicateKeyError):
            logger.error(f"Duplicate user error: {e}")
            raise HTTPException(status_code=400, detail="User with this email already exists")
        raise
    user_dict["_id"] = str(result.inserted_id)
    
    return User(**user_dict)


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login user"""
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user

@router.get("/check-admin/{workspace_id}")
async def check_admin_access(
    workspace_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Check if user is admin of workspace"""
    from app.auth.auth_handler import verify_workspace_admin
    is_admin = await verify_workspace_admin(current_user, workspace_id)
    return {"is_admin": is_admin, "user_id": current_user.id}

@router.post("/logout")
async def logout():
    """Logout user (client should remove token)"""
    return {"message": "Successfully logged out"}
