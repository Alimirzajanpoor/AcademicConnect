from fastapi import FastAPI, APIRouter, HTTPException, Depends

from crud.crud_users import (
    insert_assign_teacher_to_students,
    get_user,
    del_assign_teacher_students,
    is_followed,
    accept_follow_request,
    get_follow_request,
    reject_follow,
    request_follow,
)
from db.db_orm import AsyncDatabaseSession
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.schemas_handler import User_token
from jwt import oaut2

router_follow = APIRouter(prefix="/api/user", tags=["follow"])
session = AsyncDatabaseSession()


async def get_session():
    async with session.begin():
        yield session


@router_follow.post("/follow")
async def follow_teacher(
    teacher_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User_token = Depends(oaut2.get_current_user),
):

    user = await get_user(session, user_id=int(current_user["sub"]))
    if user.role != "student":
        raise HTTPException(403, detail="you are not student")
    if await is_followed(session, user.student.id, teacher_id):
        raise HTTPException(400, detail="already followed")
    inserted_follow = await request_follow(
        session=session,
        student_id=user.student.id,
        teacher_id=teacher_id,
    )
    await session.commit()
    if inserted_follow:
        return {"message": "follow request sent"}
    else:
        raise HTTPException(404, detail="teacher doesnt exists")


@router_follow.delete("/unfollow")
async def unfollow_teacher(
    teacher_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User_token = Depends(oaut2.get_current_user),
):

    user = await get_user(session, user_id=int(current_user["sub"]))
    if user.role != "student":
        raise HTTPException(403, detail="you are not student")
    inserted_follow = await del_assign_teacher_students(
        session=session,
        student_id=user.student.id,
        teacher_id=teacher_id,
    )
    if inserted_follow:
        return {"message": "unfollowed teacher"}
    else:
        raise HTTPException(400, detail="not followed")


@router_follow.put("/accept_follow")
async def accept_follow(
    follow_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User_token = Depends(oaut2.get_current_user),
):

    user = await get_user(session, user_id=int(current_user["sub"]))
    if user.role != "teacher":
        raise HTTPException(403, detail="you are not teacher")
    inserted_follow = await accept_follow_request(
        session=session,
        follow_id=follow_id,
    )
    if inserted_follow:
        return {"message": "accepted follow"}
    else:
        raise HTTPException(400, detail="not found")


@router_follow.get("/get_follow_requests")
async def get_follow_requests(
    session: AsyncSession = Depends(get_session),
    current_user: User_token = Depends(oaut2.get_current_user),
):

    user = await get_user(session, user_id=int(current_user["sub"]))
    if user.role != "teacher":
        raise HTTPException(403, detail="you are not teacher")

    list_of_follow_request = await get_follow_request(
        session=session, teacher_id=user.teacher.id
    )
    if list_of_follow_request:
        return list_of_follow_request
    else:
        return {"message": "no follow requests"}


@router_follow.delete("/reject_follow")
async def reject_follow_r(
    follow_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User_token = Depends(oaut2.get_current_user),
):

    user = await get_user(session, user_id=int(current_user["sub"]))
    if user.role != "teacher":
        raise HTTPException(403, detail="you are not teacher")
    inserted_follow = await reject_follow(
        session=session,
        follow_id=follow_id,
    )
    if inserted_follow:
        return {"message": "rejected follow"}
    else:
        raise HTTPException(400, detail="not found")
