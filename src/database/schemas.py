from pydantic import BaseModel


class Base(BaseModel):
    pass


class SCreateUser(Base):
    username: str
    hashed_password: str


class SCredentials(Base):
    username: str
    password: str


class SAddBook(Base):
    name: str
    author: str
    release_year: int
    ibsn: str
