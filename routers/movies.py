from fastapi import APIRouter
from pydantic import BaseModel, Field
import json
import datetime
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
    id: str
    name: str
    description: str
    photo_name: str
    user_id: int
    release_date: datetime
    genre: list[Genres]
