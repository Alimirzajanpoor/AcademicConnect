from fastapi import FastAPI, APIRouter, HTTPException, Depends
from dotenv import load_dotenv
from crud.crud_user_assign import assign_user
import os
from schemas.schemas_handler import edit_form, register_user
from crud.crud_users import (
    update_with_role,
    get_user,
    delete_user,
    user_register,
    get_user_role,
    insert_assign_teacher_to_students,
    del_assign_teacher_students,
    is_value_already_exists_teacher,
    is_value_already_exists_student,
    is_value_already_exists,
)
from db.db_orm import AsyncDatabaseSession
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.schemas_handler import assign_user_input, User_token
from jwt import oaut2

router_admin = APIRouter(prefix="/api/admin", tags=["admin"])
session = AsyncDatabaseSession()
load_dotenv()
defualt_secret_key = os.getenv("defualt_secret_key")


async def get_session():
    async with session.begin():
        yield session


@router_admin.post("/assign_user")
async def assign_user_admin_pannel(
    user_assign: assign_user_input,
    session: AsyncSession = Depends(get_session),
    current_user: User_token = Depends(oaut2.get_current_user),
):
    if await get_user_role(session, user_id=current_user["sub"]) != "admin":
        raise HTTPException(403, detail="unauthorized")
    assigned_user = await assign_user(
        session=session,
        user_id=user_assign.user_id,
        role=user_assign.role,
        age=user_assign.age,
        gender=user_assign.gender,
        rate=user_assign.rate,
        group_staff=user_assign.group_staff,
    )
    if assigned_user:
        return {"message": "user assigned"}
    else:
        raise HTTPException(400, detail="user already assigned")


@router_admin.put("/update_user")
async def update_users(
    user_update_form: edit_form,
    session: AsyncSession = Depends(get_session),
    current_user: User_token = Depends(oaut2.get_current_user),
):
    if await get_user_role(session, user_id=current_user["sub"]) != "admin":
        raise HTTPException(403, detail="unauthorized")
    updated_user = await update_with_role(
        session=session,
        user_id=user_update_form.user_id,
        username=user_update_form.username,
        first_name=user_update_form.first_name,
        last_name=user_update_form.last_name,
        password=user_update_form.password,
        age=user_update_form.age,
        role=user_update_form.role,
        gender=user_update_form.gender,
        rate=user_update_form.rate,
        national_code=user_update_form.national_code,
        group_staff=user_update_form.group_staff,
        secret_key=None,
        acsess_token=current_user,
    )
    if updated_user == 1:
        return {"message": "user updated"}
    elif updated_user == "403":
        raise HTTPException(403, detail="unauthorized")
    elif updated_user == "logout":
        return {"message": "your account info has been updated please logout"}
    elif updated_user == "username already exists":
        raise HTTPException(400, detail="username already exists")
    elif updated_user == "national_code already exists":
        raise HTTPException(400, detail="national_code already exists")
    else:
        raise HTTPException(400, detail="invalid user id")


@router_admin.get("/get_user")
async def get_users(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User_token = Depends(oaut2.get_current_user),
):
    if await get_user_role(session, user_id=current_user["sub"]) != "admin":
        raise HTTPException(403, detail="unauthorized")
    fetched_user = await get_user(session=session, user_id=user_id)
    print(current_user)
    if fetched_user:
        user_dict = fetched_user.__dict__
        user_dict.pop("password", None)
        user_dict.pop("avatar", None)
        return user_dict
    else:
        raise HTTPException(404, detail="invalid user id")


@router_admin.get("/delete_user")
async def delete_user_r(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User_token = Depends(oaut2.get_current_user),
):
    if await get_user_role(session, user_id=current_user["sub"]) != "admin":
        raise HTTPException(403, detail="unauthorized")
    deleted_user = await delete_user(session=session, user_id=user_id)
    if deleted_user:
        return {"message": "user deleted"}
    else:
        raise HTTPException(404, detail="user id not found ")


@router_admin.post("/insert_user")
async def insert_user(
    register_form: register_user,
    session: AsyncSession = Depends(get_session),
    current_user: User_token = Depends(oaut2.get_current_user),
):
    if await get_user_role(session, user_id=current_user["sub"]) != "admin":
        raise HTTPException(403, detail="unauthorized")
    inserted_user = await user_register(
        session=session,
        username=register_form.username,
        first_name=register_form.first_name,
        last_name=register_form.last_name,
        password=register_form.password,
        national_code=register_form.national_code,
    )
    await session.commit()
    if inserted_user:
        return {"message": "user inserted"}
    else:
        raise HTTPException(500, detail="an error occured during inserting user")


@router_admin.post("/assign_teacher_to_students")
async def assign_teacher_to_students_admin(
    student_id: int,
    teacher_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User_token = Depends(oaut2.get_current_user),
):
    if await get_user_role(session, user_id=current_user["sub"]) != "admin":
        raise HTTPException(403, detail="unauthorized")
    if not await is_value_already_exists_student(
        session, student_id
    ) or not await is_value_already_exists_teacher(session, teacher_id):
        raise HTTPException(400, detail="invalid userid")
    try:
        inserted_association = await insert_assign_teacher_to_students(
            session, teacher_id=teacher_id, student_id=student_id
        )

        if inserted_association:
            await session.commit()
            return {"message": "teacher and student associated"}
        else:
            await session.rollback()
            raise HTTPException(400, detail="invalid userid")
    except ValueError as e:
        print(e)
        await session.rollback()
        raise HTTPException(500, detail="Error in handling register in db")


@router_admin.delete("/del_assign_teacher_students")
async def del_assign_teacher_students_admin(
    student_id: int,
    teacher_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User_token = Depends(oaut2.get_current_user),
):
    if await get_user_role(session, user_id=current_user["sub"]) != "admin":
        raise HTTPException(403, detail="unauthorized")
    try:
        inserted_association = await del_assign_teacher_students(
            session, teacher_id=teacher_id, student_id=student_id
        )
        await session.commit()
        if inserted_association:
            return {"message": "teacher and student assocation deleted"}
        else:
            await session.rollback()
            raise HTTPException(400, detail="invalid userid")
    except ValueError as e:
        print(e)
        await session.rollback()
        raise HTTPException(500, detail="Error in handling register in db")


@router_admin.post("/create_admin")
async def create_admin(
    secret_key: str,
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
    if secret_key != defualt_secret_key:
        raise HTTPException(403, detail="unauthorized")
    inserted_user = await user_register(
        session=session,
        username=register_form.username,
        first_name=register_form.first_name,
        last_name=register_form.last_name,
        password=register_form.password,
        national_code=register_form.national_code,
    )
    await session.flush()
    if inserted_user:
        try:
            await assign_user(
                session=session,
                user_id=inserted_user["user"].id,
                role="admin",
                age=0,
                gender="male",
                rate=0,
                group_staff=None,
            )
            return {"message": "admin created"}
        except ValueError as e:

            print(e)
            await session.rollback()
        raise HTTPException(500, detail="Error in handling register in db")
    else:
        raise HTTPException(500, detail="an error occured during inserting user")
