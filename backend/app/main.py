import uvicorn
from fastapi import FastAPI
from routers import auth, materials


app = FastAPI()
# app.include_router(auth.router)
app.include_router(materials.router)
# app.include_router(topics.router)
# app.include_router(plans.router)
# app.include_router(sessions.router)

if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)