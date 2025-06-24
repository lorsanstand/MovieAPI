from fastapi import Header, HTTPException
from typing import Annotated
import json

path_movie = 'files/movie.json'
path_users = 'files/users.json'

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


def user_read():
    with open(path_users, 'r') as file:
        users_list = json.load(file)
    return users_list


def user_write(users_list):
    with open(path_users, 'w') as file:
        json.dump(users_list, file, ensure_ascii=False, indent=4)