import uuid
from typing import Any

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models import Users, UserCreate, UserUpdate,Auth

from typing import List, Optional
from sqlmodel import select, or_, col


def create_user(*, session: Session, user_create: UserCreate) -> Users:
    try:
        db_user = Users(
            nickname=user_create.nickname,
            grade=user_create.grade,
            is_admin=user_create.is_admin
        )
        session.add(db_user)
        session.flush()
        db_auth=Auth(
            identifier=user_create.identifier,
            credential=get_password_hash(user_create.credential),
            identity_type=user_create.identity_type,
            user_id=db_user.id,
            verified=True
        )
        
        session.add(db_auth)
        session.commit()
    except Exception as e:
        session.rollback()  
        raise e
    return db_user



def get_user_by_id(*, session: Session, user_id: uuid.UUID) -> Optional[Users]:
    """根据用户ID获取用户"""
    return session.get(Users, user_id)

def get_user_by_identifier(*, session: Session, identifier: str) -> Optional[Auth]:
    """根据认证标识获取认证信息（修正后的版本）"""
    statement = select(Auth).where(Auth.identifier == identifier)
    return session.exec(statement).first()

def get_users(*, session: Session, skip: int = 0, limit: int = 100) -> List[Users]:
    """获取用户列表（分页）"""
    statement = select(Users).offset(skip).limit(limit)
    return session.exec(statement).all()

def update_user(*, session: Session, db_user: Users, user_update: UserUpdate) -> Users:
    """更新用户信息"""
    user_data = user_update.dict(exclude_unset=True)
    
    # 更新用户表
    for key, value in user_data.items():
        if key == 'credential':  # 单独处理密码更新
            continue
        setattr(db_user, key, value)
    
    # 更新认证表
    if user_update.credential:
        auth = session.get(Auth, db_user.id)
        if auth:
            auth.credential = get_password_hash(user_update.credential)
    
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

def delete_user(*, session: Session, user_id: uuid.UUID) -> None:
    """删除用户及关联认证信息"""
    try:
        # 先删除认证信息
        auth = session.get(Auth, user_id)
        if auth:
            session.delete(auth)
        
        # 再删除用户
        user = session.get(Users, user_id)
        if user:
            session.delete(user)
        
        session.commit()
    except Exception as e:
        session.rollback()
        raise e

def search_users(*, session: Session, keyword: str) -> List[Users]:
    """搜索用户（昵称或标识符）"""
    statement = select(Users).join(Auth).where(
        or_(
            col(Users.nickname).ilike(f"%{keyword}%"),
            col(Auth.identifier).ilike(f"%{keyword}%")
        )
    )
    return session.exec(statement).all()

def authenticate(*, session: Session, identifier: str, password: str) -> Optional[Users]:
    """用户认证（修正版）"""
    # 获取认证信息
    auth_info = get_user_by_identifier(session=session, identifier=identifier)
    if not auth_info:
        return None
    
    # 验证密码
    if not verify_password(password, auth_info.credential):
        return None
    
    # 获取用户信息
    return get_user_by_id(session=session, user_id=auth_info.user_id)