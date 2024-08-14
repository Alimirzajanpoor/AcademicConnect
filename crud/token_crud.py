from sqlalchemy import (
    select,
    update,
)

from db.models import (
    User,
)


async def remove_token(session, token, scheduler):
    stmt = select(User).where(User.active_token == token)
    executed_token = await session.execute(stmt)
    fetched_token = executed_token.scalar_one_or_none()

    if fetched_token:
        print(fetched_token.active_token, 2)
        fetched_token.active_token = None
        await session.commit()
    scheduler.shutdown(wait=False)
    print("removed token")


async def delete_all_active_tokens(session):
    print("Deleting active tokens...")
    stmt = update(User).where(User.active_token != None).values(active_token=None)
    await session.execute(stmt)
    await session.commit()
    print("Active tokens deleted")
