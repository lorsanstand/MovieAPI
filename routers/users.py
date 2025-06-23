from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, Field
import json
from ..Dependices import check_token
from typing import Optional, Annotated

app = APIRouter(
    prefix='/users',
    tags=['users'],
    responses={404: {"description": "Not found"}}
)

path = 'files/users.json'

def user_read():
    with open(path, 'r') as file:
        users_list = json.load(file)
    return users_list

def user_write(users_list):
    with open(path, 'w') as file:
        json.dump(users_list, file, ensure_ascii=True, indent=4)


class UsersBase(BaseModel):
    nickname: str = Field(..., min_length=1, max_length=10, description='User nickname')


class UserCreate(UsersBase):
    password: str = Field(..., min_length=3, max_length=15, description='User Password')


class Users(UsersBase):
    id: int


@app.post('/')
def create_user(data: UserCreate):
    data = data.model_dump()

    users_list = user_read()

    for user in users_list:
        if user['nickname'] == data['nickname']:
            raise HTTPException(status_code=400, detail='A user with that name already exists')

    next_id = max(users_list, key=lambda x: x["id"])["id"] + 1
    data['id'] = next_id
    users_list.append(data)

    user_write(users_list)

    return {'success': True}


@app.get('/', response_model=list[Users], dependencies=[Depends(check_token)])
def get_all_users():

    users_list = user_read()

    for user in users_list:
        user.pop('password')

    return users_list


@app.get('/{user_id}', response_model=Users)
def get_user(user_id: int):

    users_list = user_read()

    for user in users_list:
        user.pop('password')

    for user in users_list:
        if user['id'] == user_id:
            return user

    raise HTTPException(status_code=404, detail='User not found')


@app.put('/{user_id}')
def editing_user(
        password: Annotated[str, Header()],
        user_id: int,
        nickname: Annotated[Optional[str], Header()] = None,
        new_password: Annotated[Optional[str], Header()] = None,
):
    if nickname is None and new_password is None:
        raise HTTPException(status_code=400, detail='Either the password or nickname must be filled in.')

    users_list = user_read()

    for user in users_list:
        if user['id'] == user_id:

            if user['password'] != password:
                raise HTTPException(status_code=400, detail='The password is incorrect')

            if nickname is not None:
                user['nickname'] = nickname

            if new_password is not None:
                user['password'] = new_password

            user_write(users_list)

            return {'success': True}

    raise HTTPException(status_code=404, detail='Id not found')


@app.delete('/{user_id}')
def delete_user(
        password: Annotated[str, Header()],
        user_id: int
):
    users_list = user_read()

    for user in users_list:
        if user['id'] == user_id:

            if user['password'] != password:
                raise HTTPException(status_code=400, detail='The password is incorrect')

            users_list.remove(user)

            user_write(users_list)

            return {'success': True}

    raise HTTPException(status_code=404, detail='Id not found')