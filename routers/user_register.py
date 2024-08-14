from fastapi import FastAPI, APIRouter, HTTPException, Depends
from crud.crud_users import user_register, is_value_already_exists
from db.db_orm import AsyncDatabaseSession
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.schemas_handler import register_user

router_register = APIRouter(prefix="/api/user", tags=["user"])
session = AsyncDatabaseSession()


async def get_session():
    async with session.begin():
        yield session


@router_register.post("/register")
async def register(
    register_form: register_user,
    session: AsyncSession = Depends(get_session),
):
    key_values = ["username", "national_code"]
    if await is_value_already_exists(session, key_values[0], register_form.username):
        await session.rollback()
        raise HTTPException(400, detail="username already exists")
    if await is_value_already_exists(
        session, key_values[1], register_form.national_code
    ):
        await session.rollback()
        raise HTTPException(400, detail="national_code already exists")
    try:
        await user_register(
            session=session,
            username=register_form.username,
            first_name=register_form.first_name,
            last_name=register_form.last_name,
            password=register_form.password,
            national_code=register_form.national_code,
        )
        await session.commit()
        return {"message": "user registered"}

    except ValueError as e:
        print(e)
        await session.rollback()
        raise HTTPException(500, detail="Error in handling register in db")
