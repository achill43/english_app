from uuid import uuid4

from config import Settings
from fastapi import HTTPException, status
from injector import Inject
from models.users import UserSQL
from pydantic import BaseModel, model_validator
from pydiator_core.interfaces import BaseResponse
from pydiator_core.mediatr import BaseRequest
from pydiator_core.mediatr_container import BaseHandler
from repositories.user_repository import UserRepository
from schemas.users import SessionReponce, UserResponse
from utils.jwt_token import generate_token, generate_token_data
from utils.password import get_hashed_password


class CreateUserRequest(BaseModel, BaseRequest):
    email: str
    first_name: str
    last_name: str
    password: str
    r_password: str

    @model_validator(mode="before")
    @classmethod
    def verify_password_match(cls, values: dict) -> dict:
        if values.get("password") != values.get("r_password"):
            raise ValueError("The passwords and r_password must be the same.")
        return values


class CreateUserResponse(BaseModel, BaseResponse):
    user: UserResponse
    session: SessionReponce


class CreateUserHandler(BaseHandler):
    def __init__(
        self, user_repository: Inject[UserRepository], settings: Inject[Settings]
    ):
        self.user_repository = user_repository
        self._settings = settings

    async def handle(self, req: CreateUserRequest) -> CreateUserResponse:
        user = await self.user_repository.get_user_by_email(email=req.email)
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exist",
            )
        user_item = req.dict()
        coded_password = get_hashed_password(req.password)
        user_item["password"] = coded_password
        del user_item["r_password"]
        user = await self.user_repository.create_user(UserSQL(**user_item))
        jti = uuid4().hex
        token_data = generate_token_data(
            user=user,
            jti=jti,
            live_time=self._settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            token_type="access",
        )
        access_token = generate_token(token_data=token_data)
        token_data = generate_token_data(
            user=user,
            jti=jti,
            live_time=self._settings.REFRESH_TOKEN_EXPIRE_MINUTES,
            token_type="refresh",
        )
        refresh_token = generate_token(token_data=token_data)
        return CreateUserResponse(
            user=UserResponse.from_orm(user),
            session=SessionReponce(
                access_token=access_token, refresh_token=refresh_token
            ),
        )
