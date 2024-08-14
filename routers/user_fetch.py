from fastapi import FastAPI, APIRouter, HTTPException, Depends

from db.models import User
import json
from crud.crud_users import get_user, read_all_teacher, get_user_role, read_all_student
from db.db_orm import AsyncDatabaseSession
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.schemas_handler import User_token
from jwt import oaut2


router_get = APIRouter(prefix="/api/user", tags=["user"])
session = AsyncDatabaseSession()


async def get_session():
    async with session.begin():
        yield session


@router_get.get("/uid")
async def get_user_id(
    id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User_token = Depends(oaut2.get_current_user),
):
    user = await get_user(session, id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user_dict = user.__dict__
    user_dict.pop("password", None)
    user_dict.pop("avatar", None)
    return user


@router_get.get("/get_current_user")
async def get_current_user_r(
    session: AsyncSession = Depends(get_session),
    current_user: User_token = Depends(oaut2.get_current_user),
):
    user = await get_user(session, int(current_user["sub"]))

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user_dict = user.__dict__
    user_dict.pop("password", None)
    user_dict.pop("avatar", None)
    return user_dict


@router_get.get("/get_all_teachers")
async def get_all_teachers_r(
    session: AsyncSession = Depends(get_session),
    current_user: User_token = Depends(oaut2.get_current_user),
):
    teachers = await read_all_teacher(session)
    if teachers:

        return teachers
    else:
        raise HTTPException(404, detail="no teachers found")


@router_get.get("/get_all_student")
async def get_all_student_r(
    session: AsyncSession = Depends(get_session),
    current_user: User_token = Depends(oaut2.get_current_user),
):
    students = await read_all_student(session)
    if students:
        return students
    else:
        raise HTTPException(404, detail="no students found")
