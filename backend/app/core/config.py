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
    PostgresDsn,
)
from pydantic_core import MultiHostUrl
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

    PROMPT_DIR:str = os.path.join(str(Path(__file__).parent.parent), "prompts")

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

    AZURE_DOCUMENT_INTELLIGENCE_KEY: str = "2cJ9tsf0Qj2mEt2l3CtkPYNYk1ma8xfZUgwJjiMnIkeSCeEXADspJQQJ99BDACYeBjFXJ3w3AAALACOGkr3h"
    AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT: str = "https://edupdfparser.cognitiveservices.azure.com/"

    AZURE_COSMOS_DB_ENDPOINT: str = "https://edudb.documents.azure.com:443/"
    AZURE_COSMOS_DB_KEY: str = "bkjswKNJNsuhp73Jwf3wUGXFjO2CudjNJRWlfd6E2t2rg4NuRIrdUcIM7xSZ0rREruYbc14EIfKiACDbCSz4rQ=="
    AZURE_COSMOS_DB_CONNECTION_STRING: str = f"AccountEndpoint={AZURE_COSMOS_DB_ENDPOINT};AccountKey={AZURE_COSMOS_DB_KEY};"
    AZURE_COSMOS_DB_DATABASE_NAME: str = "cosmosDB"

    AZURE_REDIS_HOST: str = "cacheSimclass.redis.cache.windows.net"
    AZURE_REDIS_KEY: str = "EbM9NoFTI3Z3BtU5gdYTlHOjX7hQNTs37AzCaAsrxvo="

    GLOBAL_LLM_SERVICE: str ="AzureOpenAI"
    AZURE_OPENAI_DEPLOYMENT_NAME:str ="o3-mini"
    AZURE_OPENAI_ENDPOINT:str ="https://qliu4-m9hdk661-eastus2.openai.azure.com/"
    AZURE_OPENAI_API_KEY:str ="71wikMsLTuyyHKQRlvXKI2iPpiEAXTIQrX25txbCmZ0In8niQ7eNJQQJ99BDACHYHv6XJ3w3AAAAACOG7etS"
    AZURE_OPENAI_CHAT_DEPLOYMENT_NAME:str ="o3-mini"

    AZURE_AI_ENDPOINT_DALLE:str="https://10597-ma0vw4ue-swedencentral.services.ai.azure.com"
    AZURE_AI_KEY_DALLE:str="FN5q7kRKygIhhbfi7o2n41bP0qURfHvwPMVmveLnQKYN07ddR9BtJQQJ99BDACfhMk5XJ3w3AAAAACOGH37x"
    AZURE_AI_DALLE_NAME:str="dall-e-3"

    # Set endpoints and API keys for Azure services
    AZURE_SEARCH_SERVICE: str = "PUT YOUR SEARCH SERVICE URL HERE"
    AZURE_SEARCH_KEY: str = "DELETE IF USING ROLES, OTHERWISE PUT YOUR SEARCH SERVICE ADMIN KEY HERE"
    AZURE_AI_MULTISERVICE_ACCOUNT: str = "PUT YOUR AZURE AI MULTISERVICE ACCOUNT URL HERE"
    AZURE_AI_MULTISERVICE_KEY: str = "PUT YOUR AZURE AI MULTISERVICE KEY HERE. ROLES ARE USED TO CONNECT. KEY IS USED FOR BILLING."
    AZURE_STORAGE_CONNECTION: str = "PUT YOUR AZURE STORAGE CONNECTION STRING HERE (see example below for syntax)"

    SERPAPI_KEY:str="50c31eafdd3dd64245daba39a216c557"


    POSTGRES_SERVER: str="localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str="postgres"
    POSTGRES_PASSWORD: str = "Hackathon123"
    POSTGRES_DB: str = "postgres"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

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
        self._check_default_secret("POSTGRES_PASSWORD", self.POSTGRES_PASSWORD)
        self._check_default_secret(
            "FIRST_SUPERUSER_PASSWORD", self.FIRST_SUPERUSER_PASSWORD
        )
        return self


settings = Settings()  # type: ignore
