from fastapi import APIRouter, HTTPException, Depends
from crud.crud_ban import ban_user, unban_user
from crud.crud_users import get_user_role
from db.db_orm import AsyncDatabaseSession
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.schemas_handler import User_token
from jwt import oaut2


router_ban = APIRouter(prefix="/api/ban_student", tags=["ban"])
session = AsyncDatabaseSession()


async def get_session():
    async with session.begin():
        yield session


@router_ban.put("/ban_user")
async def ban_student(
    user_id: int,
    current_user: User_token = Depends(oaut2.get_current_user),
):

    if (
        await get_user_role(session, int(current_user["sub"])) == "teacher"
        or await get_user_role(session, int(current_user["sub"])) == "admin"
    ):

        banned_user = await ban_user(session, user_id)
        if banned_user:
            return {"message": "user banned"}
        else:
            raise HTTPException(400, detail="invalid userid")

    else:
        raise HTTPException(403, detail="unauthorized")


@router_ban.put("/unban_user")
async def unban_student(
    user_id: int,
    current_user: User_token = Depends(oaut2.get_current_user),
):
    # try:
    print(current_user["user_role"], "<---")
    if (
        await get_user_role(session, int(current_user["sub"])) == "teacher"
        or await get_user_role(session, int(current_user["sub"])) == "admin"
    ):

        unbanned_user = await unban_user(session, user_id)
        if unbanned_user:
            return {"message": "user unbanned"}
        else:
            raise HTTPException(400, detail="invalid userid")

    else:
        raise HTTPException(403, detail="unauthorized")
