from sqlalchemy.ext.asyncio import (
    async_session, AsyncEngine, create_async_engine, async_sessionmaker)
from .models import Base
from dotenv import load_dotenv
import os


load_dotenv()


engine = create_async_engine(os.getenv("SQLITE_DB_URL"))
async_session = async_sessionmaker(engine)


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
