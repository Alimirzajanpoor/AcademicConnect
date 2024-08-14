from fastapi import APIRouter, Depends, status, HTTPException, Security, Response
from fastapi.security import OAuth2PasswordRequestForm
from utl_handler.hash import Hash
from utl_handler.scheduler_handler import schedule_job
from db.db_orm import AsyncDatabaseSession
from db.models import User
from sqlalchemy import select, or_
from jwt.oaut2 import get_current_user
from jwt.token_handler import create_access_token, get_refresh_token
from sqlalchemy.ext.asyncio import AsyncSession
import contextlib

router_login = APIRouter(
    tags=["authentication"],
    prefix="/api/authentication",
)


session = AsyncDatabaseSession()


async def get_session():
    try:
        async with session.begin():
            yield session
    except Exception as e:
        print(f"An error occurred: {e}")


@router_login.post("/login")
async def login(
    response: Response,
    request: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_session),
):

    stmt = select(User).filter(
        or_(
            User.username == request.username,
            str(User.national_code) == request.username,
        )
    )
    user = await db.execute(stmt)
    db_user = user.scalar_one_or_none()

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid Credentials"
        )

    if not Hash.verify(db_user.password, request.password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="incorrect password"
        )
    data = {
        "sub": str(db_user.id),
    }
    access_token = await create_access_token(data=data)

    response.set_cookie(key="access_token", value=access_token)
    return access_token


@router_login.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh_access_token(
    refresh_token: str, db: AsyncSession = Depends(get_session)
):
    return await get_refresh_token(
        token=refresh_token,
        credentials_exception=HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ),
        session=db,
    )


@router_login.post("/logout")
async def logout(
    response: Response,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    stmt = select(User).filter(User.id == int(current_user["sub"]))
    user = await db.execute(stmt)
    db_user = user.scalar_one_or_none()

    if db_user:
        response.delete_cookie(key="access_token")

        db_user.active_token = None
        await db.commit()

    return {"message": "Logged out successfully"}
