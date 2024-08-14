from fastapi import FastAPI, Depends
from dotenv import load_dotenv
from routers.user_register import router_register
from routers.login import router_login
from routers.assign_user import router_assign
from routers.comment_handler import router_comment
from routers.ban_handler import router_ban
from routers.admin_pannel import router_admin
from routers.user_fetch import router_get
from routers.follow_teacher import router_follow
from routers.avatar_router import router_avatar
from db.db_orm import AsyncDatabaseSession
from sqlalchemy import inspect
from db.models import Students
from sqlalchemy.ext.asyncio import AsyncSession
from routers.edit_profile import router_edit


app = FastAPI()

session = AsyncDatabaseSession()


async def get_session():
    async with session.begin():
        yield session


@app.get("/info")
async def root():
    return {"message": "Hello, World!"}


@app.on_event("startup")
async def startup():

    # await db.create_all()
    # studets_test = Students(firstname="Mazust", last_name="Mazustov", is_banned=False)
    await session.create_all()
    table_names = await session.get_table_names()
    print(table_names)

    print("Starting up...")


@app.on_event("shutdown")
async def shutdown():
    print("Shutting down...")

    # await db.close()


# deploying routers
app.include_router(router_admin)
app.include_router(router_register)
app.include_router(router_login)
app.include_router(router_assign)
app.include_router(router_get)
app.include_router(router_edit)
app.include_router(router_comment)
app.include_router(router_ban)
app.include_router(router_follow)
app.include_router(router_avatar)
