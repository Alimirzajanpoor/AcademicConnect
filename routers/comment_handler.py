from fastapi import FastAPI, APIRouter, HTTPException, Depends
from crud.crud_ban import is_student_banned
from crud.crud_users import get_user_role, is_followed, get_user
from crud.crud_comment import insert_comment
from db.db_orm import AsyncDatabaseSession
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.schemas_handler import comment_user, User_token
from jwt import oaut2

router_comment = APIRouter(prefix="/api/comment", tags=["comments"])
session = AsyncDatabaseSession()


async def get_session():
    async with session.begin():
        yield session


@router_comment.post("/add")
async def insert_comment_r(
    comment_form: comment_user,
    session: AsyncSession = Depends(get_session),
    current_user: User_token = Depends(oaut2.get_current_user),
):

    try:
        if await get_user_role(session, int(current_user["sub"])) == "student":

            if await is_student_banned(session, user_id=int(current_user["sub"])):
                raise HTTPException(403, detail="you are banned")
            if await get_user_role(session, comment_form.receiver_id) != "teacher":
                raise HTTPException(403, detail="reciver should be teacher")
            fetched_student = await get_user(session, user_id=int(current_user["sub"]))
            fetched_teacher = await get_user(session, user_id=comment_form.receiver_id)
            if not await is_followed(
                session,
                student_id=fetched_student.student.id,
                teacher_id=fetched_teacher.teacher.id,
            ):
                raise HTTPException(403, detail="you are not followed")
        inserted_comment = await insert_comment(
            session,
            comment=comment_form.content,
            receiver=comment_form.receiver_id,
            sender=int(current_user["sub"]),
        )
        if inserted_comment:
            return {"message": "comment inserted"}
        else:
            raise HTTPException(403, detail="you should be student")
    except ValueError as e:
        print(e)
        await session.rollback()
        raise HTTPException(500, detail="Error in handling comments in db")
