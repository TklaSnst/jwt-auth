from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .models import User
from .schemas import SCreateUser


class DBUserTable():
    def __init__(self, async_session: AsyncSession):
        self.async_session = async_session

    async def get_by_id(self, uid: int) -> User | None:
        async with self.async_session() as session:
            try:
                stmt = select(User).where(User.uid == uid)
                result = await session.execute(stmt)
                user = result.scalar()
                return user
                print(user)
            except Exception as e:
                return None
            
    async def get_by_username(self, username: str) -> User | None:
        async with self.async_session() as session:
            try:
                stmt = select(User).where(User.username == username)
                result = await session.execute(stmt)
                user = result.scalar()
                return user
            except Exception as e:
                return None
            
    async def create_one(self, user: SCreateUser) -> int | None:
        async with self.async_session() as session:
            try:
                user_create = User(**user.model_dump())
                session.add(user_create)
                await session.commit()
                return user_create.uid
            except Exception as e:
                return None

    async def update_refresh_token(self, uid: int, new_refresh_token: str) -> int | None:
        async with self.async_session() as session:
            try:
                stmt = select(User).where(User.uid == uid)
                result = await session.execute(stmt)    
                user = result.scalar()
                user.jwt_refresh_token = new_refresh_token
                await session.commit()
                return 1
            except Exception as e:
                return None
            