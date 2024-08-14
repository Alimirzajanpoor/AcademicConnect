from db.models import User, User_comments
from crud.crud_user_assign import assign_user
from datetime import datetime
from utl_handler.hash import Hash
from sqlalchemy import select


async def is_value_already_exists(db, table, column_name, value):
    stmt = select(table).where(getattr(table, column_name) == value)
    result = await db.execute(stmt)

    exists = result.first() is not None

    return exists


async def insert_comment(session, comment, receiver, sender):
    if await is_value_already_exists(session, User, "id", receiver):

        inserted_comment = User_comments(
            content=comment, receiver=receiver, sender=sender
        )
        session.add(inserted_comment)
        await session.commit()
        return 1
    else:
        return 0
