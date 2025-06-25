from fastapi import FastAPI

from .routers import users, movies, reviews

app = FastAPI()

app.include_router(users.app)
app.include_router(movies.app)
app.include_router(reviews.app)