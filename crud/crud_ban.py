from db.models import User, Students
from sqlalchemy import select
from utl_handler.hash import Hash


async def is_value_already_exists(db, table, column_name, value):
    stmt = select(table).where(getattr(table, column_name) == value)
    result = await db.execute(stmt)

    exists = result.first() is not None

    return exists


async def ban_user(session, user_id):
    stmt = select(Students).where(Students.user_id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if user:
        user.is_banned = True
        await session.commit()
        return 1
    else:
        return 0


async def unban_user(session, user_id):
    stmt = select(Students).where(Students.user_id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if user:
        user.is_banned = False
        await session.commit()
        return 1
    else:
        return 0


async def is_student_banned(session, user_id):
    stmt = select(Students).where(Students.user_id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if user:
        return user.is_banned
    else:
        return 0
