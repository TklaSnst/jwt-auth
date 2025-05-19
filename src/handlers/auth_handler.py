from fastapi import APIRouter, Request, Response
from fastapi.responses import RedirectResponse
from src.database import user_manager
from src.database.token_manager import token_manager
from src.database.schemas import SCreateUser, SCredentials
import hashlib


router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


def hash_string(str: str):
    """
    Returns hashed hexdigest string
    """
    hash_obj = hashlib.new('sha256')
    hash_obj.update(str.encode())
    hashed_str = hash_obj.hexdigest()
    return hashed_str


@router.post("/get-pair-tokens")
async def set_pair_tokens(uid: int, request: Request):
    tokens = await token_manager.get_pair_tokens(uid)
    return tokens


@router.post("/registration")
async def registration(credentials: SCredentials, request: Request, response: Response):
    username = credentials.username
    password = credentials.password
    db_user = await user_manager.get_by_username(username=username)
    if db_user:
        return RedirectResponse("/login")
        # return f"User {username} is already exist Try to log-in"
    hashed_password = hash_string(password)
    user_create = SCreateUser(username=username, hashed_password=hashed_password)
    created_uid = await user_manager.create_one(user=user_create)
    if not created_uid:
        return "Something went wrong"
    
    new_tokens = await token_manager.get_pair_tokens(id=created_uid)
    result = user_manager.update_refresh_token(
        uid=created_uid,
        new_refresh_token = new_tokens.get("jwt_access_token"),
    )
    if not result:
        return "something went wrong"
    await token_manager.update_cookies(
        uid=created_uid,
        new_refresh_token = new_tokens.get("jwt_refresh_token"),
        new_access_token= new_tokens.get("jwt_access_token"),
        response=response
    )
    return f"Hello, {username}"
    

@router.post("/login")
async def login(credentials: SCredentials, request: Request, response: Response):
    username = credentials.username
    password = credentials.password
    db_user = await user_manager.get_by_username(username=username)
    print(db_user)
    hashed_password = hash_string(password)
    if db_user.hashed_password != hashed_password:
        return "Wrong username or password"
    new_tokens = await token_manager.get_pair_tokens(id=db_user.uid)    
    await token_manager.update_cookies(
        uid=db_user.uid,
        response=response,
        new_access_token=new_tokens.get("jwt_access_token"),
        new_refresh_token=new_tokens.get("jwt_refresh_token"),
    )
    await user_manager.update_refresh_token(
        uid=db_user.uid,
        new_refresh_token=new_tokens.get("jwt_refresh_token")
    )
    return f"Hello, {username}"