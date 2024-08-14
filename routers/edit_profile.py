from fastapi import FastAPI, APIRouter, HTTPException, Depends
from crud.crud_users import edit_user
from db.db_orm import AsyncDatabaseSession
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.schemas_handler import edit_form, User_token
from jwt import oaut2

router_edit = APIRouter(prefix="/api/user", tags=["user"])
session = AsyncDatabaseSession()


async def get_session():
    async with session.begin():
        yield session


@router_edit.put("/edit_profile")
async def edit_profile(
    edit_form: edit_form,
    current_user: User_token = Depends(oaut2.get_current_user),
):
    try:

        edited_user = await edit_user(
            session,
            user_id=int(current_user["sub"]),
            username=edit_form.username,
            first_name=edit_form.first_name,
            password=edit_form.password,
            last_name=edit_form.last_name,
            national_code=edit_form.national_code,
            age=edit_form.age,
            gender=edit_form.gender,
            group_staff=edit_form.group_staff,
            rate=edit_form.rate,
            role=edit_form.role,
        )
        if edited_user:
            return {"message": "user edited"}
        raise HTTPException(status_code=400, detail="userid not founds")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
