from fastapi import FastAPI
from app.routers import stage4

app = FastAPI()

app.include_router(stage4.router)

@app.get("/")
def read_root():
    return {"message": "Hello, this is the Stage4 API!"}
