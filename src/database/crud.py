from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from .models import User, Book, BorrowedBooks
from .schemas import SCreateUser, SAddBook
from .database import async_session
from datetime import date


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
            

class BookCrud():
    def __init__(self, async_session: AsyncSession) -> int | None:
        self.async_session = async_session
    
    async def get_one_data(self, book_id: int) -> Book | None:
        async with self.async_session() as session:
            try:
                stmt = select(Book).where(Book.id == book_id)
                result = await session.execute(stmt)
                book = result.scalar()
                return book
            except Exception as e:
                return None
            
    async def borrow_one(self, book_id: int, user_id: int) -> int | None:
        async with self.async_session() as session:
            try:
                stmt = (select(BorrowedBooks)
                        .where(BorrowedBooks.user_id == user_id, 
                               BorrowedBooks.return_date.is_(None))
                    )
                result = await session.execute(stmt)
                if len(result.scalars().all()) > 3:
                    return -1

                stmt = select(Book).where(Book.id == book_id)
                result = await session.execute(stmt)
                book = result.scalar()
                book.count -= 1
                new_record = BorrowedBooks(
                    user_id=user_id, book_id=book_id, borrow_date=date.today()
                    )
                session.add(new_record)
                await session.commit()
                return book.id
            except Exception as e:
                return None    
            
    async def return_one(self, book_id: int, user_id: int):
        async with async_session() as session:
            try:
                stmt = ( 
                    select(BorrowedBooks)
                    .where(BorrowedBooks.book_id == book_id)
                    .where(BorrowedBooks.user_id == user_id)
                    .order_by(desc(BorrowedBooks.id))
                    .limit(1)
                )
                result = await session.execute(stmt)
                borrow_record = result.scalar()
                borrow_record.return_date = date.today()
                stmt = select(Book).where(Book.id == book_id)
                result = await session.execute(stmt)
                book = result.scalar()
                book.count += 1
                await session.commit()
                return 1
            except Exception as e:
                return None
    
    async def get_all(self):
        async with self.async_session() as session:
            stmt = select(Book)
            result = await session.execute(stmt)
            books = result.scalars().all()
            return books

    async def add_one(self, book: SAddBook):
        async with self.async_session() as session:
            async with session.begin():
                try:
                    insert = Book(**book.model_dump())
                    session.add(insert)
                    await session.flush()
                    return insert.id
                except Exception as e:
                    await session.rollback()
                    print(e)
                    return None


user_manager = DBUserTable(async_session=async_session)
book_manager = BookCrud(async_session=async_session)
