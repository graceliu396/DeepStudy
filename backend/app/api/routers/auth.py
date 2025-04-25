from datetime import timedelta
from typing import Annotated, Any
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from app import crud
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
    existing_user = crud.get_user_by_identifier(session=session, email=user_create.identifier)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # db_user = User.model_validate(user_create)
    db_user=Users(
        nickname=user_create.nickname,
        avatar_url=user_create.avatar_url
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    hashed_passwd=get_password_hash(user_create.credential)
    db_auth=Auth(
        identifier=user_create.identifier,
        credential=hashed_passwd,
        identity_type=user_create.identity_type,
        user_id=db_user.id,
        verified=False
    )

    session.add(db_auth)
    session.commit()
    session.refresh(db_auth)

    try:
        token=generate_email_activation_token(email=user_create.identifier)
        email_data=generate_email_activation_email(email_to=user_create.identifier, username=user_create.nickname, token=token)
        send_email(email_to=user_create.identifier, subject=email_data.subject, html_content=email_data.html_content)
    except Exception as e:
        #TODO 错误恢复，删除数据库中新创建的user
        raise HTTPException(status_code=500, detail=str(e))

    return db_user

@router.post("/activate-account")
def activate_email(
    session: SessionDep,
    token: str
):
    email = verify_token(token=token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    
    auth=crud.get_user_by_identifier(session=session, email=email)
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
    user = crud.authenticate(session=session, account=form_data.identifier, password=form_data.password)
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
    user = crud.get_user_by_email(session=session, email=email)

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
    user = crud.get_user_by_email(session=session, email=email)
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
    user = crud.get_user_by_email(session=session, email=email)

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



