from fastapi import FastAPI

from .routers import users

app = FastAPI()

app.include_router(users.app)
# app.include_router(movies.app)