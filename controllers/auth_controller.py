from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from config.security import create_password, encode_token, verify_password
from controllers.base_controller import BaseController
from models.auth_model import UserModel
from schema.auth_schema import UserCreateRequest, UserLoginRequest, UserLoginResponse


class AuthController(BaseController):
    def __init__(self, session: AsyncSession):
        super().__init__(session, UserModel)

    async def create(self, data: UserCreateRequest):
        user_exists = await self._get_by(email=data.email)

        # user_exists = (
        #     await self.session.execute(
        #         select(UserModel).where(UserModel.email == data.email)
        #     )
        # ).scalar_one_or_none()
        if user_exists:
            raise HTTPException(
                status_code=400, detail="user already exist. please login"
            )
        user = UserModel(
            **data.model_dump(exclude={"password"}),
            password=create_password(data.password),
        )
        user = await self._add(user)
        # self.session.add(user)
        # await self.session.commit()
        # await self.session.refresh(user)
        token = encode_token(
            {"id": str(user.id), "name": user.name, "email": user.email}
        )

        return UserLoginResponse(**user.model_dump(), access_token=token)

    async def login(self, data: UserLoginRequest):
        user = await self._get_by(email=data.email)
        # user = (
        #     await self.session.execute(
        #         select(UserModel).where(UserModel.email == data.email)
        #     )
        # ).scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=400, detail="user not found. please try latter"
            )
        user_verify = verify_password(data.password, user.password)
        if not user_verify:
            raise HTTPException(
                status_code=400, detail="user verify failed. please try latter"
            )
        token = encode_token(
            {"id": str(user.id), "name": user.name, "email": user.email}
        )
        return UserLoginResponse(**user.model_dump(), access_token=token)
