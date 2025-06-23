from fastapi import APIRouter, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, field_validator
# import json
from datetime import datetime, date
from enum import Enum

app = APIRouter(
    prefix='/movies',
    tags=['movies'],
    responses={404: {"description": "Not found"}}
)


class Genres(str, Enum):
    fantasy = 'Фантастика'
    science_fiction = 'Научная фантастика'
    documentary = "Документальный фильм"
    historical = "Исторический фильм"
    horror = "Хоррор"
    detective = "Детектив"
    drama = "Драма"
    romance = "Роман"
    comedy = "Комедия"



class MoviesBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=30, description='Movie name')
    description: str = Field(..., min_length=1, max_length=500, description='Movie description')
    user_id: int = Field(..., description='Id of the user who added the movie')
    release_date: datetime = Field(..., description='Release date')
    genre: list[Genres] = Field(..., description='Genres')

    @field_validator("release_date")
    def validate_release_date(cls, values: date):
        if values and values >= datetime.now().date():
            raise ValueError('Дата рождения должна быть в прошлом')
        return values


class MovieCreate(MoviesBase):
    id: str
    photo: UploadFile = Field(..., description='Movie cover')


    @field_validator('photo')
    def validate_photo(cls, values: UploadFile):
        format_photo = ('.jpg', '.png')

        if not values.filename.endswith(format_photo):
            raise ValueError('Photo format must be jpg or png')
        return values




class Movies(MoviesBase):
    photo: FileResponse = Field(..., description="Movie cover")