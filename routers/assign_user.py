from fastapi import FastAPI, APIRouter, HTTPException, Depends
from crud.crud_user_assign import assign_user
from crud.crud_users import (
    insert_assign_teacher_to_students,
    del_assign_teacher_students,
)
from db.db_orm import AsyncDatabaseSession
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.schemas_handler import assign_user_input, User_token
from jwt import oaut2

router_assign = APIRouter(prefix="/api/user", tags=["user"])
session = AsyncDatabaseSession()


async def get_session():
    async with session.begin():
        yield session


@router_assign.put("/assign_user")
async def assign_user_r(
    assign_form: assign_user_input,
    session: AsyncSession = Depends(get_session),
    current_user: User_token = Depends(oaut2.get_current_user),
):
    try:
        print(assign_form.role)
        assigned_user = await assign_user(
            session,
            user_id=int(current_user["sub"]),
            age=assign_form.age,
            role=assign_form.role,
            gender=assign_form.gender,
            rate=assign_form.rate,
            group_staff=assign_form.group_staff,
        )
        # await session.commit()
        if assigned_user:
            return {"message": "user assigned"}

        else:
            await session.rollback()
            raise HTTPException(400, detail="invalid userid")
    except ValueError as e:
        print(e)
        await session.rollback()
        raise HTTPException(500, detail="Error in handling register in db")
