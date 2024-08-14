from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import token_handler
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.db_orm import db
from db.models import User
from jose import JWTError, jwt


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/authentication/login")
session = db


async def get_session():
    async with session.begin():
        yield session


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    async for session_obj in get_session():
        decoded_token = await token_handler.verify_token(
            token, credentials_exception, session_obj
        )

        return decoded_token
