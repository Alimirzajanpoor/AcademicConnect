from fastapi import APIRouter, HTTPException, Depends, UploadFile
from crud.avatar_crud import (
    insert_avatar,
    delete_avatar,
    update_avatar,
    get_avatars,
    set_current_avatar,
    get_current_avatar,
    get_avatar,
)
import zipfile
import io
from fastapi.responses import StreamingResponse
from db.db_orm import AsyncDatabaseSession
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.schemas_handler import User_token, AvatarURLs
from jwt import oaut2


router_avatar = APIRouter(prefix="/api/avatar", tags=["avatar"])
session = AsyncDatabaseSession()


async def get_session():
    async with session.begin():
        yield session


@router_avatar.post("/upload_avatar")
async def upload_avatar(
    image: UploadFile,
    current_user: User_token = Depends(oaut2.get_current_user),
    session: AsyncSession = Depends(get_session),
):
    uploaded_avatar = await insert_avatar(session, image, int(current_user["sub"]))
    if uploaded_avatar:
        await session.commit()
        return {"message": "avatar uploaded"}

    else:
        raise HTTPException(400, detail="avatar upload failed")


@router_avatar.put("/set_current_avatar")
async def set_current_avatar_r(
    id: int,
    current_user: User_token = Depends(oaut2.get_current_user),
    session: AsyncSession = Depends(get_session),
):
    current_avatar = await set_current_avatar(
        session=session, owner_id=int(current_user["sub"]), id=id
    )
    if current_avatar:
        return {"message": "avatar set"}
    else:
        raise HTTPException(400, detail="invalid id")


@router_avatar.get("/get_current_avatar")
async def get_current_avatar_r(
    current_user: User_token = Depends(oaut2.get_current_user),
    session: AsyncSession = Depends(get_session),
):
    current_avatar = await get_current_avatar(session, int(current_user["sub"]))
    if current_avatar:
        return StreamingResponse(
            io.BytesIO(current_avatar.avatar), media_type="image/jpeg"
        )

    else:
        raise HTTPException(400, detail="invalid id")


@router_avatar.put("/update_avatar")
async def update_avatar_r(
    image: UploadFile,
    id: int,
    current_user: User_token = Depends(oaut2.get_current_user),
    session: AsyncSession = Depends(get_session),
):
    updated_avatar = await update_avatar(session, id, image)
    if updated_avatar:
        await session.commit()
        return {"message": "avatar updated"}

    else:
        raise HTTPException(400, detail="avatar update failed")


@router_avatar.delete("/delete_avatar")
async def delete_avatar_r(
    id: int,
    current_user: User_token = Depends(oaut2.get_current_user),
    session: AsyncSession = Depends(get_session),
):
    deleted_avatar = await delete_avatar(session, id)
    if deleted_avatar:
        await session.commit()
        return {"message": "avatar deleted"}
    else:
        raise HTTPException(400, detail="invalid id")


@router_avatar.get("/get_an_avatar")
async def get_avatar_r(
    id: int,
    current_user: User_token = Depends(oaut2.get_current_user),
    session: AsyncSession = Depends(get_session),
):
    current_avatar = await get_avatar(session, id)
    if current_avatar:
        return StreamingResponse(
            io.BytesIO(current_avatar.avatar), media_type="image/jpeg"
        )

    else:
        raise HTTPException(400, detail="invalid id")


@router_avatar.get("/get_avatars")
async def get_avatars_r(
    current_user: User_token = Depends(oaut2.get_current_user),
    session: AsyncSession = Depends(get_session),
):
    avatars = await get_avatars(session, int(current_user["sub"]))
    avatar_urls = []
    if avatars:
        for ids in avatars:

            avatar_url = f"127.0.0.1:8000:/api/avatar/get_an_avatar?id={ids.id}"
            avatar_urls.append(avatar_url)

        return AvatarURLs(urls=avatar_urls)

    else:
        raise HTTPException(400, detail="avatars not found")
