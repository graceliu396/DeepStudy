import secrets
import warnings
import os
from typing import Annotated, Any, Literal
from pathlib import Path

from pydantic import (
    AnyUrl,
    BeforeValidator,
    EmailStr,
    HttpUrl,
    computed_field,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self
from sqlalchemy import create_engine
import urllib


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_ignore_empty=True,
        extra="ignore",
    )
    
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    FRONTEND_HOST: str = "http://localhost:5173"
    # ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    PROMPT_DIR:str = os.path.join(str(Path(__file__).parent), "prompts")

    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [
            self.FRONTEND_HOST
        ]

    PROJECT_NAME: str = "simclass"
    SENTRY_DSN: HttpUrl | None = None
    AZURE_SQL_SERVER_NAME: str = "mysqlserver0412.database.windows.net"
    AZURE_SQL_DATABASE_NAME: str = "user_db"
    AZURE_SQL_USER_NAME: str = "simclass_admin"
    AZURE_SQL_PASSWORD: str = "Hackathon123"
    DRIVER:str ="{ODBC Driver 18 for SQL Server}"

    connection_string:str = f"DRIVER={DRIVER}; \
        SERVER=tcp:{AZURE_SQL_SERVER_NAME},1433; \
        DATABASE={AZURE_SQL_DATABASE_NAME}; \
        UID={AZURE_SQL_USER_NAME}; \
        PWD={AZURE_SQL_PASSWORD}; \
        Encrypt=yes; \
        TrustServerCertificate=no; \
        Connection Timeout=30"
    connection_string:str = urllib.parse.quote_plus(connection_string)
    SQLALCHEMY_DATABASE_URI:str = 'mssql+pyodbc:///?odbc_connect=' + connection_string

    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_PORT: int = 587
    SMTP_HOST: str = "smtp.qq.com"
    SMTP_USER: str ="1059752643@qq.com"
    SMTP_PASSWORD: str ="scsecgegfzkqbcia"
    EMAILS_FROM_EMAIL: EmailStr ="1059752643@qq.com"
    EMAILS_FROM_NAME: str ="Simclass-EDU"

    @model_validator(mode="after")
    def _set_default_emails_from(self) -> Self:
        if not self.EMAILS_FROM_NAME:
            self.EMAILS_FROM_NAME = self.PROJECT_NAME
        return self

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48

    @computed_field  # type: ignore[prop-decorator]
    @property
    def emails_enabled(self) -> bool:
        return bool(self.SMTP_HOST and self.EMAILS_FROM_EMAIL)

    EMAIL_TEST_USER: EmailStr = "test@example.com"
    FIRST_SUPERUSER: EmailStr = "1059752643@qq.com"
    FIRST_SUPERUSER_PASSWORD: str = "12345678"

    def _check_default_secret(self, var_name: str, value: str | None) -> None:
        if value == "changethis":
            message = (
                f'The value of {var_name} is "changethis", '
                "for security, please change it, at least for deployments."
            )
            if self.ENVIRONMENT == "local":
                warnings.warn(message, stacklevel=1)
            else:
                raise ValueError(message)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        self._check_default_secret("SECRET_KEY", self.SECRET_KEY)
        self._check_default_secret("AZURE_SQL_PASSWORD", self.AZURE_SQL_PASSWORD)
        self._check_default_secret(
            "FIRST_SUPERUSER_PASSWORD", self.FIRST_SUPERUSER_PASSWORD
        )
        return self


settings = Settings()  # type: ignore
