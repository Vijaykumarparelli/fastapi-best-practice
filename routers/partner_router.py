from fastapi import APIRouter

from config.redis import token_blacklist
from config.security import GetPartnerFromToken
from deps.partner_dep import PartnerControllerDep, PartnerLoginFormData
from schema.partner_schema import (
    PartnerCreateRequest,
    PartnerLoginRequest,
    PartnerLoginResponse,
    PartnerResponse,
)

router = APIRouter(prefix="/partner", tags=["partner"])


@router.post("/create", response_model=PartnerLoginResponse)
async def create_partner(data: PartnerCreateRequest, ctrl: PartnerControllerDep):
    return await ctrl.create(data)


@router.post("/login", response_model=PartnerLoginResponse)
async def partner_login(data: PartnerLoginRequest, ctrl: PartnerControllerDep):
    return await ctrl.login(data)


@router.post("/token", response_model=PartnerLoginResponse)
async def login_from_form(data: PartnerLoginFormData, ctrl: PartnerControllerDep):
    return await ctrl.login(
        PartnerLoginRequest(email=data.username, password=data.password)
    )


@router.get("/me", response_model=PartnerResponse)
async def get_logged_in_partner(data: GetPartnerFromToken):
    return data


@router.get("/logout")
async def logout_partner(data: GetPartnerFromToken):
    await token_blacklist(data.jti, data.exp)
    return "partner logout success"
