from datetime import timedelta
from typing import Annotated, Any
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from app.tools.sql_crud import *
from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.core.config import settings
from app.core.security import *
from app.models import *
from app.utils import (
    generate_password_reset_token,
    generate_reset_password_email,
    generate_email_activation_token,
    generate_email_activation_email,
    send_email,
    verify_token,
)

router = APIRouter(tags=["login"])

@router.post("/register", response_model=UserPublic)
def register(
    session: SessionDep,
    user_create: UserCreate):
    # 检查用户是否存在
    existing_user = get_user_by_identifier(session=session, email=user_create.identifier)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    try:
        # 创建用户和认证记录（原子操作）
        db_user = Users(
            nickname=user_create.nickname,
            grade=user_create.grade,
            is_admin=False
        )
        session.add(db_user)
        session.flush()  # 生成用户ID但不提交

        # 创建认证信息
        hashed_passwd = get_password_hash(user_create.credential)
        db_auth = Auth(
            identifier=user_create.identifier,
            credential=hashed_passwd,
            identity_type=user_create.identity_type,
            user_id=db_user.id,
            verified=False
        )
        session.add(db_auth)
        session.commit()  # 统一提交用户和认证记录
        
        # 发送激活邮件
        token = generate_email_activation_token(email=user_create.identifier)
        email_data = generate_email_activation_email(
            email_to=user_create.identifier,
            username=user_create.nickname,
            token=token
        )
        send_email(
            email_to=user_create.identifier,
            subject=email_data.subject,
            html_content=email_data.html_content
        )
    
    except Exception as e:
        # 错误恢复逻辑
        session.rollback()  # 回滚未提交的操作
        
        # 如果用户已创建但未提交
        if 'db_user' in locals():
            # 删除可能已提交的记录
            session.exec(Users).filter(Users.id == db_user.id).delete()
            session.exec(Auth).filter(Auth.user_id == db_user.id).delete()
            session.commit()
            
        raise HTTPException(
            status_code=500,
            detail="Registration failed, please try again later"
        )
    
    return db_user

@router.post("/activate-account")
def activate_email(
    session: SessionDep,
    token: str
):
    email = verify_token(token=token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    
    auth=get_user_by_identifier(session=session, email=email)
    if not auth:
        raise HTTPException(status_code=404, detail="User not found")
    if auth.verified == True:
        raise HTTPException(status_code=400, detail="Email has already been activated")
    auth.verified = True
    session.add(auth)
    session.commit()
    session.refresh(auth)
    return Message(message="Email activated successfully")
    

@router.post("/login/email")
def login(
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = authenticate(session=session, identifier=form_data.identifier, password=form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect account or password")
    if user.verified == False:
        raise HTTPException(status_code=400, detail="Email is not activated yet")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=create_access_token(
            user.id, expires_delta=access_token_expires
        )
    )


@router.post("/password-recovery/{email}")
def recover_password(email: str, session: SessionDep) -> Message:
    """
    Password Recovery
    """
    user = get_user_by_identifier(session=session, identifier=email)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system.",
        )
    password_reset_token = generate_password_reset_token(email=email)
    email_data = generate_reset_password_email(
        email_to=user.email, username=user.nickname, token=password_reset_token
    )
    send_email(
        email_to=user.email,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    return Message(message="Password recovery email sent")


@router.post("/reset-password/")
def reset_password(session: SessionDep, body: NewPassword) -> Message:
    """
    Reset password
    """
    email = verify_token(token=body.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = get_user_by_identifier(session=session, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system.",
        )
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    hashed_password = get_password_hash(password=body.new_password)
    user.hashed_password = hashed_password
    session.add(user)
    session.commit()
    return Message(message="Password updated successfully")


@router.post(
    "/password-recovery-html-content/{email}",
    dependencies=[Depends(get_current_active_superuser)],
    response_class=HTMLResponse,
)
def recover_password_html_content(email: str, session: SessionDep) -> Any:
    """
    HTML Content for Password Recovery
    """
    user = get_user_by_identifier(session=session, email=email)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    password_reset_token = generate_password_reset_token(email=email)
    email_data = generate_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token
    )

    return HTMLResponse(
        content=email_data.html_content, headers={"subject:": email_data.subject}
    )



#TODO @router.post("/login/google", response_model=Token)
#TODO @router.post("/login/microsoft", response_model=Token)



