from pydantic import BaseModel, EmailStr
from datetime import date


class SUserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    
class SPostBase(BaseModel):
    title: str
    description: str
    
class SPostCreate(SPostBase):
    category_id: int
    
class SPostResponse(SPostBase):
    username: str
    category_name: str 
    
    class Config:
        from_attributes  = True

    