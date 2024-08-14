from db.models import Avatars
from sqlalchemy import select, and_
import zipfile
from io import BytesIO


async def insert_avatar(session, image, owner_id):
    if image != None:
        readed_image = await image.read()
    else:
        readed_image = None
    does_current_exists = await session.execute(
        select(Avatars).where(
            and_(Avatars.is_current == True, Avatars.owner_id == owner_id)
        )
    )
    does_current_exists = does_current_exists.scalar()
    if does_current_exists:
        inserted_avatar = Avatars(
            owner_id=owner_id,
            avatar=readed_image,
            is_current=False,
        )
    else:
        inserted_avatar = Avatars(
            owner_id=owner_id,
            avatar=readed_image,
            is_current=True,
        )

    session.add(inserted_avatar)

    return 1


async def update_avatar(session, id, image):
    if image != None:
        readed_image = await image.read()
    else:
        readed_image = None
    existing_file = await session.execute(select(Avatars).where(Avatars.id == id))

    existing_file = existing_file.scalar()
    if existing_file:
        existing_file.avatar = readed_image
        session.add(existing_file)
        return 1
    return 0


async def set_current_avatar(session, owner_id, id):
    does_current_exists = await session.execute(
        select(Avatars).where(
            and_(Avatars.is_current == True, Avatars.owner_id == owner_id)
        )
    )
    does_current_exists = does_current_exists.scalar()
    if does_current_exists:
        does_current_exists.is_current = False
    existing_file = await session.execute(select(Avatars).where(Avatars.id == id))
    existing_file = existing_file.scalar()
    if existing_file:
        existing_file.is_current = True
        return 1
    else:
        return 0


async def get_current_avatar(session, id):
    existing_file = await session.execute(
        select(Avatars).where(and_(Avatars.is_current == True, Avatars.owner_id == id))
    )
    existing_file = existing_file.scalar()
    if existing_file:
        return existing_file
    else:
        return None


async def delete_avatar(session, id):
    existing_file = await session.execute(select(Avatars).where(Avatars.id == id))
    existing_file = existing_file.scalar()
    if existing_file:

        await session.delete(existing_file)
        return 1
    else:

        return 0


async def get_avatar(session, query):
    stmt = select(Avatars).where(Avatars.id == query)
    result = await session.execute(stmt)
    fetched_avatars = result.scalar()
    if fetched_avatars:
        return fetched_avatars
    else:
        return 0


async def get_avatars(session, query):
    stmt = select(Avatars).where(Avatars.owner_id == query)
    result = await session.execute(stmt)
    fetched_avatars = result.scalars().all()
    if fetched_avatars:
        return fetched_avatars
    else:
        return 0
