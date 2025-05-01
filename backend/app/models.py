from datetime import datetime
from typing import List, Optional, Literal
from sqlmodel import Field, Relationship, SQLModel, Column, UniqueConstraint, Index
from sqlalchemy import DateTime, func
import sqlalchemy as sa

GradeLevel = Literal["K", "1", "2", "3", "4", "5", "6", "7", "8", "H"]

grade_check = sa.CheckConstraint(
    "grade IN ('K', '1', '2', '3', '4', '5', '6', '7', '8', 'H')",
    name="valid_grade_check"
)


class UserBase(SQLModel):
    nickname: str = Field(max_length=50, nullable=False)
    grade: GradeLevel = Field(
        sa_column=Column(
            sa.VARCHAR(2),  # 数据库存储为字符串
            nullable=False,
            info={"check_constraint": grade_check}
        )
    )
    is_admin: bool = Field(default=False)


class UserCreate(UserBase):
    identity_type: str = Field(max_length=20)
    identifier: str = Field(max_length=255)
    credential: str = Field(min_length=8, max_length=40)


class UserUpdate(SQLModel):
    nickname: Optional[str] = Field(max_length=50)
    grade: GradeLevel = Field(
        sa_column=Column(
            sa.VARCHAR(2),  
            nullable=False,
            info={"check_constraint": grade_check}
        )
    )


class Users(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    )
    
    auths: List["Auth"] = Relationship(back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"})


class AuthBase(SQLModel):
    identity_type: str = Field(max_length=20)
    identifier: str = Field(max_length=255)
    credential: Optional[str] = Field(max_length=512)
    verified: bool = Field(default=False)


class Auth(AuthBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    
    user: Users = Relationship(back_populates="auths")
    
    __table_args__ = (
        UniqueConstraint("identity_type", "identifier"),
        Index("idx_identity", "identity_type", "identifier"),
    )




class UserPublic(UserBase):
    id: int
    grade: GradeLevel
    created_at: datetime
    updated_at: datetime

# 用户列表响应
class UsersPublic(SQLModel):
    data: List[UserPublic]
    count: int

# 登录请求模型
class UserLogin(SQLModel):
    identity_type: str = Field(max_length=20)
    identifier: str = Field(max_length=255)
    credential: str = Field(min_length=8, max_length=40)

# Token响应模型
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"

# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None

class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)

# 修改密码请求
class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)

# 通用消息响应
class Message(SQLModel):
    message: str