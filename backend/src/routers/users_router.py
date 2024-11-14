from depends.auth_deps import get_current_user
from fastapi import APIRouter, Depends
from pydiator_core.mediatr import pydiator
from schemas.users import UserResponse
from use_cases.users.create_user import CreateUserRequest
from use_cases.users.user_login import UserLoginRequest

users_router = APIRouter(prefix="/users")


@users_router.post("/sign_up/", summary="Create new user")
async def sign_up(req: CreateUserRequest):
    return await pydiator.send(req=req)


@users_router.post("/sign_in/", summary="Login in system")
async def sign_in(req: UserLoginRequest):
    return await pydiator.send(req=req)


@users_router.get(
    "/me/",
    summary="Get details of currently logged in user",
    response_model=UserResponse,
)
async def get_me(user: UserResponse = Depends(get_current_user)):
    return user
