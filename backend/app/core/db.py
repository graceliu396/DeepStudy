from sqlmodel import Session, create_engine, select

from app.tools import sql_crud
from sqlmodel import SQLModel
from app.core.config import settings
from app.models import Users, UserCreate, Auth

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI), pool_pre_ping=True)


def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # This works because the models are already imported and registered from app.models
    SQLModel.metadata.create_all(engine)

    user = session.exec(
        select(Auth).where(Auth.identifier == settings.FIRST_SUPERUSER)
    ).first()
    if not user:
        user_in = UserCreate(
            identity_type="email",
            identifier=settings.FIRST_SUPERUSER,
            credential=settings.FIRST_SUPERUSER_PASSWORD,
            nickname="admin",
            grade="H",
            is_admin=True
        )
        user = sql_crud.create_user(session=session, user_create=user_in)

# init_db()