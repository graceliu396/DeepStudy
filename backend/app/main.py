import os
import sys
from pathlib import Path
print(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent))
import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware
from app.api.main import api_router
from app.core.config import settings
import logging
from sqlmodel import Session
from app.core.db import engine, init_db
from app.api.routers.session import subapi
from chainlit.utils import mount_chainlit


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"





app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

@subapi.get("/sub")
def read_sub():
    return {"message": "Hello World from sub API"}


app.mount("/subapi", subapi)
mount_chainlit(app, r"D:\Programming\AIAgent\SemanticKernel\hackathon\simclass\backend\app\agent\stage1_teaching_chainlit.py", "/chainlit/session_936cb00d-ffdf-42e1-a0da-202a404b219e")

# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)

def init() -> None:
    with Session(engine) as session:
        init_db(session)


def start_app() -> None:
    logger.info("Creating initial data")
    init()
    logger.info("Initial data created")
    uvicorn.run(
        app="main:app",    # 等价于命令行中的 main:app
        host="0.0.0.0",    # 开放外部访问
        port=80,           # 监听80端口
        # 可选附加参数
        reload=False,      # 生产环境应关闭热重载
    )

if __name__ == "__main__":
    start_app()
    

