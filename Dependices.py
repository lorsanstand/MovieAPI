from fastapi import Header, HTTPException
from typing import Annotated

def check_token(token: Annotated[str, Header()]):
    if token != '123456':
        raise HTTPException(status_code=400, detail='Has token invalid')