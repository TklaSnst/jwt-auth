from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Column, DateTime, ForeignKey
from datetime import date


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    uid: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    jwt_refresh_token: Mapped[str] = mapped_column(nullable=True)


class Book(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    author: Mapped[str] = mapped_column(nullable=False)
    release_year: Mapped[int] = mapped_column(nullable=True)
    ibsn: Mapped[str] = mapped_column(unique=True)
    count: Mapped[int] = mapped_column(default=1)   


class BorrowedBooks(Base):
    __tablename__ = "registrations"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.uid), nullable=False)
    book_id: Mapped[int] = mapped_column(ForeignKey(Book.id), nullable=False)
    borrow_date: Mapped[date] = mapped_column(nullable=False)
    return_date: Mapped[date] = mapped_column(default=None, nullable=True)
