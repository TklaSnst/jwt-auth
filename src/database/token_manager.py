from authx import AuthX, AuthXConfig
from jwt.exceptions import ExpiredSignatureError
from src.database import user_manager
from fastapi import Response
import jwt
import os


class TokenManager():
    """
    Class disigned for manage JWT tokens. Requires JWT_SECRET_KEY enviroment variable.
    """   
    def __init__(self):
        self.config = AuthXConfig()
        self.config.JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
        self.config.JWT_ACCESS_COOKIE_NAME = "jwt_access_token"
        self.config.JWT_REFRESH_COOKIE_NAME = "jwt_refresh_token"
        self.security = AuthX(config=self.config)

    async def validate_token(self, token) -> dict | None:
        """
        Tries to validate token, returns token {payload} or None if token is expired 
        """
        try:
            payload = jwt.decode(
                token,
                os.getenv("JWT_SECRET_KEY"),
                algorithms=["HS256"],
            )
            return payload
        except ExpiredSignatureError:
            return None
        
    async def validate_user(self, response: Response, jwt_access_token: str, jwt_refresh_token: str) -> dict | None:
        token_data = await self.validate_token(token=jwt_access_token)
        if token_data:
            return token_data
        uid = await self.get_id_from_access_token(jwt_access_token=jwt_access_token)
        user = await user_manager.get_by_id(uid=uid)
        if (not user) or (user.jwt_refresh_token != jwt_refresh_token):
            return None
        new_tokens = await self.get_pair_tokens(id=uid)
        result = await self.update_cookies(
            uid=uid,
            response=response,
            new_access_token=new_tokens.get("jwt_access_token"),
            new_refresh_token=new_tokens.get("jwt_refresh_token")
        )
        if not result:
            return None
        return result      

    async def get_id_from_access_token(self, jwt_access_token) -> int | None:
        try:
            payload = self.validate_token(jwt_access_token)
            uid: int = payload.get("sub")
            return uid
        except Exception as e:
            return None

    async def get_pair_tokens(self, id: int) -> dict:
        access_token = self.security.create_access_token(uid=str(id))
        refresh_tooken = self.security.create_refresh_token(uid=str(id))
        return{
            "id": id,
            "jwt_access_token": access_token,
            "jwt_refresh_token": refresh_tooken,
        }

    async def update_cookies(
            self, uid: int, response: Response, new_access_token: str, new_refresh_token: str
        ) -> dict | None:
        """
        Tries to update both browser JWT cookies.
        Returns dict of jwt tokens or None in case of errors. 
        """
        try:
            response.delete_cookie("jwt_access_token")
            response.delete_cookie("jwt_refresh_token")

            response.set_cookie(self.config.JWT_ACCESS_COOKIE_NAME, new_access_token, httponly=True)
            response.set_cookie(self.config.JWT_REFRESH_COOKIE_NAME, new_refresh_token, httponly=True)

            return{
                "id": uid,
                "jwt_access_token": new_access_token,
                "jwt_refresh_token": new_refresh_token,
            }
        except Exception as e:
            return None
        

token_manager = TokenManager()