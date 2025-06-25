from pydantic import BaseModel, Field, model_validator, field_validator
from fastapi import APIRouter, HTTPException, Header

from .users import UsersBase
from ..Dependices import movie_read, user_read, review_read, review_write
from typing import Annotated

app = APIRouter(
    prefix='/reviews',
    tags=['reviews'],
    responses = {404: {"description": "Not found"}}
)


class ReviewBase(BaseModel):
    movie_id: int = Field(..., description='ID of the movie reviewed')
    grade: int = Field(..., le=5, ge=1, description='Grade from 1 to 5')
    description: str = Field(..., min_length=1, max_length=500, description='description')

    @field_validator('movie_id')
    def validate_movie_id(cls, values):
        if not any(movie['id'] for movie in movie_read()):
            raise HTTPException(status_code=404, detail='Movie not found')
        return values


class Review(ReviewBase):
    id: int
    user_id: int = Field(..., description='User who left a review')


class UserCheck(BaseModel):
    nickname: Annotated[str, Header()] = Field(description='User nickname')
    password: Annotated[str, Header()] = Field(description='User password')

    @field_validator('nickname')
    def validate_user(cls, nickname):
        if nickname in (user['nickname'] for user in user_read()):
            return nickname
        raise HTTPException(status_code=404, detail='User not found')

    @model_validator(mode='before')
    def validate_password(cls, values):
        nickname = values.get('nickname')
        password = values.get('password')

        if any(password == user['password'] for user in user_read() if nickname in user['nickname']):
            return values

        raise HTTPException(status_code=400, detail='password incorrect')



@app.post('/')
def create_review(review: ReviewBase, user_l: UserCheck):
    reviews_list = review_read()
    review_dict = review.model_dump()
    next_id = max(reviews_list, key=lambda reviews: reviews['id'])['id'] + 1
    user_id = next(user['id'] for user in user_read() if user['nickname'] == user_l.nickname)

    review_dict['id'] = next_id
    review_dict['user_id'] = user_id
    reviews_list.append(review_dict)
    review_write(reviews_list)

    return {'success': True}

@app.get('/{movie_id}', response_model=list[Review])
def get_reviews(movie_id: int):
    reviews_list = [review for review in review_read() if review['movie_id'] == movie_id]
    return reviews_list