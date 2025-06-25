from fastapi import APIRouter, UploadFile, File, HTTPException, Header, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime, date
from enum import Enum
from typing import Self, Annotated
from ..Dependices import movie_write, movie_read, user_read, check_token

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
    combat = "Боевик"



class MoviesBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=30, description='Movie name')
    description: str = Field(..., min_length=1, max_length=500, description='Movie description')
    release_date: date = Field(..., description='Release date in format YYYY-MM-DD')
    genre: list[Genres] = Field(..., description='Genres')

    @field_validator("release_date")
    def validate_release_date(cls, values: date) -> Self:
        if values and values >= datetime.now().date():
            raise HTTPException(status_code=400, detail='Release date should be in the past')
        return values


class MoviesCreate(MoviesBase):
    @field_validator('name')
    def validate_name(cls, name: str):
        if name in (movie['name'] for movie in movie_read()):
            raise HTTPException(status_code=400, detail='A movie with this title has already been added')
        return name


class Movies(MoviesBase):
    id: int
    user_id: int = Field(..., description='Id of the user who added the movie')


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
def create_movie(movie: MoviesCreate, user: UserCheck):
    movie_dict = movie.model_dump()
    print(movie)
    movies_list = movie_read()
    users_list = user_read()
    user_id = next(userdb['id'] for userdb in users_list if user.nickname == userdb['nickname'])
    next_id = max(movies_list, key=lambda movie_id: movie_id['id'])['id'] + 1

    movie_dict['id'] = next_id
    movie_dict['user_id'] = user_id
    movie_dict['release_date'] = movie_dict['release_date'].strftime('%Y-%m-%d')

    movies_list.append(movie_dict)
    movie_write(movies_list)

    return {'Success': True}


@app.get('/', response_model=list[Movies])
def get_page_movies(page: int, num: int):
    movies = movie_read()
    return movies[page*num:page*num+num]


@app.post('/film/{movie_id}/cover')
def upload_cover(movie_id: int, cover: UploadFile = File(..., description='Cover to movie')):
    movies_dict = movie_read()
    if not 'image' in cover.content_type:
        raise HTTPException(status_code=400, detail='Photo format must be jpg or png')

    for movie in movies_dict:
        if movie['id'] == movie_id:
            with open(f'files/photo/{movie['name']}.jpg', 'wb') as file:
                file.write(cover.file.read())

    return {'Success': True}


@app.get('/film/{movie_id}/cover')
def download_cover(movie_id: int):
    movie = next(movie for movie in movie_read() if movie_id == movie['id'])
    return FileResponse(path=f'files/photo/{movie["name"]}.jpg', filename='cover.jpg')


@app.get('/all', response_model=list[Movies], dependencies=[Depends(check_token)])
def get_all_movies():
    return movie_read()


@app.get('/{movie_id}', response_model=Movies)
def get_movie(movie_id: int):
    return next(movie for movie in movie_read() if movie_id == movie['id'])


@app.put('/{movie_id}')
def update_movie(movie_id: int, new_movie: MoviesCreate):
    movies = movie_read()
    new_movie = new_movie.model_dump()
    movie = next(movie for movie in movies if movie_id == movie['id'])

    if not any(movie_id == movie['id'] for movie in movies if movie_id == movie['id']):
        raise HTTPException(status_code=404, detail='Movie not found')

    new_movie['id'] = movie_id
    new_movie['user_id'] = movie['user_id']
    new_movie['release_date'] = new_movie['release_date'].strftime('%Y-%m-%d')

    movies.remove(movie)
    movies.append(new_movie)
    movie_write(movies)

    return {'Success': True}


@app.delete('/{movie_id}', dependencies=[Depends(check_token)])
def delete_movie(movie_id: int):
    movies = movie_read()
    movie = next(movie for movie in movies if movie_id == movie['id'])

    movies.remove(movie)
    movie_write(movies)

    return {'Success': True}