from fastapi import APIRouter

from config.redis import token_blacklist
from config.security import GetToken, GetUserFromToken
from deps.auth_dep import AuthControllerDep
from schema.auth_schema import (
    UserCreateRequest,
    UserLoginFormData,
    UserLoginRequest,
    UserLoginResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/create", response_model=UserLoginResponse)
async def create_user(data: UserCreateRequest, ctrl: AuthControllerDep):
    return await ctrl.create(data)


@router.post("/login", response_model=UserLoginResponse)
async def login_user(data: UserLoginRequest, ctrl: AuthControllerDep):
    return await ctrl.login(data)


@router.post("/token")
async def login_with_form(data: UserLoginFormData, ctrl: AuthControllerDep):
    print(data)
    return await ctrl.login(
        UserLoginRequest(email=data.username, password=data.password)
    )


@router.get("/me", response_model=UserResponse)
def get_user_me(data: GetUserFromToken):
    return data


@router.get("/logout")
async def logout_user(data: GetUserFromToken):
    await token_blacklist(data.jti, data.exp)
    return {"message": "logout_user success!"}
