from fastapi import APIRouter, Request, Response
from src.database import book_manager, user_manager
from src.database.token_manager import token_manager
from fastapi.responses import RedirectResponse
from src.database.schemas import SAddBook
import json

router = APIRouter(
    prefix = "/lib",
    tags = ["librarian"]
)


@router.post("/borrow-book")
async def borrow_book(book_id: int, request: Request, response: Response):
    book = await book_manager.get_one_data(book_id=book_id)
    if not book:
        return "There is no such book"
    if book.count < 1:
        return "There is no books left"
    jwt_access_token = request.cookies.get("jwt_access_token")
    jwt_refresh_token = request.cookies.get("jwt_refresh_token")
    user_validation = await token_manager.validate_user(
        response=response, jwt_access_token=jwt_access_token, jwt_refresh_token=jwt_refresh_token
    )
    if not user_validation:
        return RedirectResponse("http://127.0.0.1:8000/login")
    borrow_res = book_manager.borrow_one(id=token_manager.get_id_from_access_token(jwt_access_token))
    if not borrow_res:
        return "Something went wrong"
    elif borrow_res == -1:
        return "You cant borrow more than 3 books in one time"
    return f"You successfully borowwed a book. Name - {book.name}, author - {book.author}"


@router.post("/add-book")
async def add_book(book: SAddBook):
    inserted_id = await book_manager.add_one(book=book)
    if not inserted_id:
        return "Smthng went wrong"
    return f"Book has been added, id-{inserted_id}"


@router.post("/return-book")
async def return_book(book_id: int, request: Request, response: Response):
    user_validation = await token_manager.validate_user(
        response=response,
        jwt_access_token=request.cookies.get("jwt_access_token"),
        jwt_refresh_token=request.cookies.get("jwt_refresh_token"),
        )
    if not user_validation:
        return RedirectResponse("http://127.0.0.1:8000/login")
    uid = await token_manager.get_id_from_access_token(
        jwt_access_token=request.cookies.get("jwt_access_token")
    )
    res = await book_manager.return_one(book_id=book_id, user_id=uid)
    if not res:
        return "Something went wrong"
    return "The book has been returned successfuly"


@router.get("/get-all-books")
async def get_all_books():
    return await book_manager.get_all()
