from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    nickname: str
    avatar_url: str = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class GoogleToken(BaseModel):
    id_token: str