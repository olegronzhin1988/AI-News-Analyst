# main.py file, contains app instance and main function

from fastapi import FastAPI
import uvicorn
from contextlib import asynccontextmanager
from database import init_db
from routers.analysis import analysis_router


# Decorated function for lifespan app, to activate db
# on server/app start
@asynccontextmanager
async def lifespan(app:FastAPI):
    await init_db()
    print("SQLite DB activated")
    yield
    print("SQLite DB deactiveted")

# Creating app
app = FastAPI(lifespan=lifespan,
              title="AI News Analyst",
              description="FastAPI + AI service, collects fresh news on topic",
              version="1.0.0")

# Connecting analysis router
app.include_router(analysis_router)

# Default root endpoint
@app.get("/")
async def root():
    return ({"message":"You`re on AI News Analyst frontpage"})

# App autostart with uvicorn
if __name__=="__main__":
    uvicorn.run("main:app",
                host="127.0.0.1",
                port=8000,
                reload=True)