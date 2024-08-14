from jose import JWTError, jwt
from datetime import datetime, timedelta
from schemas.schemas_handler import TokenResponse
from utl_handler.scheduler_handler import schedule_job
import os
from dotenv import load_dotenv
from db.models import User
from sqlalchemy import select


load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))


def create_refresh_token(data):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


async def create_access_token(data: dict, refresh_token=None):

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    time_remaining_seconds = (expire - datetime.utcnow()).total_seconds()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    if not refresh_token:
        refresh_token = create_refresh_token(data)

    return TokenResponse(
        access_token=encoded_jwt,
        refresh_token=refresh_token,
        expires_in=time_remaining_seconds,
    )


async def get_refresh_token(token, credentials_exception, session):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id = payload.get("sub", None)

        if user_id is None:
            raise credentials_exception

        stmt = select(User).filter(User.id == int(user_id))
        user = await session.execute(stmt)
        db_user = user.scalar_one_or_none()
        if db_user is None:
            raise credentials_exception

        return await create_access_token(session, data=payload, refresh_token=token)
    except JWTError as e:
        print(e)
        raise credentials_exception


async def verify_token(token: str, credentials_exception, session):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id = payload.get("sub", None)

        if user_id is None:
            raise credentials_exception

        exp_timestamp = payload.get("exp")
        if exp_timestamp is None or exp_timestamp < datetime.utcnow().timestamp():
            raise credentials_exception
        stmt = select(User).filter(User.id == int(user_id))
        user = await session.execute(stmt)
        db_user = user.scalar_one_or_none()
        if db_user is None:  # or db_user.active_token != token:
            raise credentials_exception

        return payload
    except JWTError:
        raise credentials_exception
