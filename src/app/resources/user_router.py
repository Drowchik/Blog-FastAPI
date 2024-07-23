from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import parse_obj_as
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.models import User
from src.app.schemas.shemas import SUserRegister
from src.app.core.database import async_session_maker, get_db
from src.app.services.auth import create_access_token, create_user, get_current_user, get_password_hash, get_user_by_filter, verify_password
from src.app.tasks.tasks import send_confirmation_email


router = APIRouter(prefix="/auth", tags=["Auth & Пользователи"],)

@router.post("/register")
async def register_user(user_data: SUserRegister, db: AsyncSession = Depends(get_db)):
    existing_user = await get_user_by_filter(db, email=user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hash_password = get_password_hash(user_data.password)
    await create_user(db=db, 
                      email=user_data.email, 
                      hashed_password=hash_password, 
                      name=user_data.name)
    user_dict = parse_obj_as(SUserRegister, user_data).dict()
    send_confirmation_email.delay(user_dict, user_data.email)
    return user_dict
    

@router.post("/login")
async def login_user(response: Response, user_data: SUserRegister, db: AsyncSession = Depends(get_db)):
    existing_user = await get_user_by_filter(db, email=user_data.email)
    if not existing_user and not verify_password(user_data.password, existing_user.hashed_password):
        raise HTTPException(status_code=400, detail="Email not registered")
    access_token = create_access_token({"sub": str(existing_user.id)})
    response.set_cookie("access_token_blog", access_token, httponly=True)

@router.post("/logout")
async def logout_user(response: Response):
    response.delete_cookie("access_token_blog")
    return {"message": "Logged out successfully."}
    
@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user