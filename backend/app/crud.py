import uuid
from typing import Any

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models import Users, UserCreate, UserUpdate,Auth


def create_user(*, session: Session, user_create: UserCreate) -> Users:
    db_user = Users.model_validate(user_create)
    db_auth=Auth(
        identifier=user_create.identifier,
        credential=get_password_hash(user_create.password),
        identity_type=user_create.identity_type,
        user_id=db_user.id,
        verified=True
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    session.add(db_auth)
    session.commit()
    session.refresh(db_auth)
    return db_user



def get_user_by_identifier(*, session: Session, email: str) -> Users | None:
    statement = select(Auth).where(Auth.identifier == email)
    session_user = session.exec(statement).first()
    return session_user


def authenticate(*, session: Session, email: str, password: str) -> Users | None:
    db_user = get_user_by_identifier(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.credential):
        return None
    return db_user

