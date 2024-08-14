from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import MetaData
import os

load_dotenv()

SQLALCHAMY_DATABASE_URL = os.getenv("DATABASE_URL")

print(SQLALCHAMY_DATABASE_URL)
Base = declarative_base()


class AsyncDatabaseSession:
    def __init__(self):
        self.engine = create_async_engine(
            SQLALCHAMY_DATABASE_URL,
            future=True,
            echo=False,
            # turned off logging; if you can't identify a problem, set this to True
        )

        self.session = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )()

    def __getattr__(self, name):
        return getattr(self.session, name)

    async def create_all(self):
        print("Creating tables...")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def get_table_names(self):
        async with self.engine.connect() as conn:
            metadata = MetaData()
            await conn.run_sync(metadata.reflect)
            return metadata.tables.keys()


db = AsyncDatabaseSession()
