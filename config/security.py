from datetime import datetime, timedelta, timezone
from typing import Annotated
from uuid import UUID, uuid4

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash

from config.db import DBSession
from config.redis import is_token_blacklist
from config.settings import settings
from models.auth_model import UserModel
from models.partner_model import PartnerModel
from schema.auth_schema import UserResponse

_pwd_hash = PasswordHash.recommended()

from schema.partner_schema import PartnerResponse
from schema.shipment_schema import ShipmentResponse


def create_password(password: str) -> str:
    return _pwd_hash.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return _pwd_hash.verify(password, hashed)


def encode_token(data: dict, expAt: timedelta = timedelta(days=1)) -> str:
    exp = datetime.now(timezone.utc) + expAt
    return jwt.encode(
        {**data, "exp": exp, "jti": str(uuid4())},
        key=settings.JWT_SECRET,
        algorithm=settings.JWT_ALGO,
    )


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(
            token, key=settings.JWT_SECRET, algorithms=[settings.JWT_ALGO]
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="ExpiredSignatureError")
    except jwt.InvalidSignatureError:
        raise HTTPException(status_code=401, detail="InvalidSignatureError")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="InvalidTokenError")


oauth_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", scheme_name="UserAuth")
GetToken = Annotated[str, Depends(oauth_scheme)]


async def verify_user_with_token(token: GetToken, session: DBSession):
    if not token:
        raise HTTPException(status_code=401, detail="invalid token")
    data = decode_token(token)
    is_blocked = await is_token_blacklist(data["jti"])
    if is_blocked:
        raise HTTPException(
            status_code=401, detail="user user_verify_failed token_blacklist"
        )
    user = await session.get(UserModel, UUID(data["id"]))
    if not user:
        raise HTTPException(status_code=401, detail="user user_verify_failed")
    return UserTokenData(
        **user.model_dump(),
        exp=data["exp"],
        jti=data["jti"],
        # shipment=[
        #     ShipmentResponse.model_validate(shipment).model_dump()
        #     for shipment in user.shipment
        # ],
    )


class UserTokenData(UserResponse):
    exp: int
    jti: UUID
    # shipment: list[ShipmentResponse] = []


GetUserFromToken = Annotated[UserTokenData, Depends(verify_user_with_token)]

partner_oauth_scheme = OAuth2PasswordBearer(
    tokenUrl="/partner/token", scheme_name="PartnerAuth"
)
GETPartnerToken = Annotated[str, Depends(partner_oauth_scheme)]


async def get_partner_by_token(token: GETPartnerToken, session: DBSession):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    data = decode_token(token)
    is_blocked = await is_token_blacklist(data["jti"])
    if is_blocked:
        raise HTTPException(
            status_code=401, detail="partner user_verify_failed token_blacklist"
        )
    partner = await session.get(PartnerModel, UUID(data["id"]))
    if not partner:
        raise HTTPException(status_code=401, detail="partner partner_verify_failed")
    return PartnerTokenUser(**partner.model_dump(), exp=data["exp"], jti=data["jti"])


class PartnerTokenUser(PartnerResponse):
    exp: int
    jti: UUID


GetPartnerFromToken = Annotated[PartnerTokenUser, Depends(get_partner_by_token)]
