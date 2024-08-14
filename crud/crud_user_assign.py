from db.models import User, Teachers, Students
from sqlalchemy import select
from utl_handler.hash import Hash


async def is_value_already_exists(db, table, column_name, value):
    stmt = select(table).where(getattr(table, column_name) == value)
    result = await db.execute(stmt)

    exists = result.first() is not None

    return exists


async def assign_user(session, user_id, role, age, gender, rate, group_staff):
    stmt = select(User).where(User.id == user_id)
    existing_user = await session.execute(stmt)
    existing_user = existing_user.scalar_one_or_none()
    print(role)
    print(existing_user.gender)
    if existing_user:
        existing_user.role = role
        existing_user.age = age
        existing_user.gender = gender
        if role == "teacher":
            if not await is_value_already_exists(
                session, Teachers, "user_id", user_id
            ) and not await is_value_already_exists(
                session, Students, "user_id", user_id
            ):
                inserting_teacher = Teachers(
                    user_id=user_id,
                    group_staff=group_staff,
                    rate=rate,
                )
                session.add(inserting_teacher)
            else:

                return 0
        if role == "student":
            if not await is_value_already_exists(
                session, Students, "user_id", user_id
            ) and not await is_value_already_exists(
                session, Teachers, "user_id", user_id
            ):

                inserting_student = Students(
                    user_id=user_id,
                )
                session.add(inserting_student)
            else:
                return 0
        await session.commit()
        return 1
    else:
        return 0
