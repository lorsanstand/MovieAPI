from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, field_validator
import json
from datetime import datetime, date
from enum import Enum

app = APIRouter(
    prefix='/movies',
    tags=['movies'],
    responses={404: {"description": "Not found"}}
)

path = 'files/movie.json'


def movie_read() -> list:
    with open(path, 'r') as file:
        movie_list = json.load(file)
    return movie_list


def movie_write(movie_list: list):
    with open(path, 'w') as file:
        json.dump(movie_list, file, ensure_ascii=False, indent=4)


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
    release_date: date = Field(..., description='Release date in format YYYY-MM-DD')
    genre: list[Genres] = Field(..., description='Genres')

    @field_validator("release_date")
    def validate_release_date(cls, values: date):
        if values and values >= datetime.now().date():
            raise ValueError('Release date should be in the past')
        return values

    @field_validator('name')
    def validate_name(cls, name: str):
        if name in (movie['name'] for movie in movie_read()):
            raise ValueError('A movie with this title has already been added')


class Movies(MoviesBase):
    id: str
    # photo: FileResponse = Field(..., description="Movie cover")
    user_id: int = Field(..., description='Id of the user who added the movie')


@app.post('/')
def create_movie(movie: MoviesBase):
    # format_cover = ('png', 'jpg')
    # print(cover.content_type)
    # if not cover.filename.endswith(format_cover):
    #     raise ValueError('Photo format must be jpg or png')
    #
    # with open(movie.name + '.jpg', 'wb') as file:
    #     file.write(cover.content_type)

    movie_dict = movie.model_dump()
    movies_list = movie_read()
    next_id = max(movies_list, key=lambda movie_id: movie_id['id'])['id'] + 1

    movie_dict['id'] = next_id
    movie_dict['release_date'] = movie_dict['release_date'].strftime('%Y-%m-%d')
    movies_list.append(movie_dict)
    movie_write(movies_list)

    return {'Success': True}



