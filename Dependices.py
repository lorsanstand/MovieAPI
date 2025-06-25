from fastapi import Header, HTTPException
from typing import Annotated
import json

path_movie = 'files/movie.json'
path_users = 'files/users.json'
path_reviews = 'files/reviews.json'

def check_token(token: Annotated[str, Header()]):
    if token != '123456':
        raise HTTPException(status_code=400, detail='Has token invalid')

def movie_read() -> list:
    with open(path_movie, 'r') as file:
        movie_list = json.load(file)
    return movie_list


def movie_write(movie_list: list):
    with open(path_movie, 'w') as file:
        json.dump(movie_list, file, ensure_ascii=False, indent=4)


def user_read() -> list:
    with open(path_users, 'r') as file:
        users_list = json.load(file)
    return users_list


def user_write(users_list: list):
    with open(path_users, 'w') as file:
        json.dump(users_list, file, ensure_ascii=False, indent=4)


def review_read() -> list:
    with open(path_reviews, 'r') as file:
        users_list = json.load(file)
    return users_list


def review_write(review_list: list):
    with open(path_reviews, 'w') as file:
        json.dump(review_list, file, ensure_ascii=False, indent=4)