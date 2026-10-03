from fastapi import HTTPException
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from config.security import create_password, encode_token, verify_password
from controllers.base_controller import BaseController
from models.partner_model import PartnerModel
from schema.partner_schema import (
    PartnerCreateRequest,
    PartnerLoginRequest,
    PartnerLoginResponse,
)


class PartnerController(BaseController):
    def __init__(self, session: AsyncSession):
        super().__init__(session, PartnerModel)

    async def create(self, data: PartnerCreateRequest):
        partner_exists = await self._get_by(email=data.email)
        # partner_exists = (
        #     await self.session.execute(
        #         Select(PartnerModel).where(PartnerModel.email == data.email)
        #     )
        # ).scalar_one_or_none()
        if partner_exists:
            raise HTTPException(
                status_code=400, detail="partner already exist. please login"
            )
        partner = PartnerModel(
            **data.model_dump(exclude={"password"}),
            password=create_password(data.password),
        )
        partner = await self._add(partner)
        # self.session.add(partner)
        # await self.session.commit()
        # await self.session.refresh(partner)
        token = encode_token(
            {"id": str(partner.id), "email": partner.email, "name": partner.name}
        )
        return PartnerLoginResponse(**partner.model_dump(), access_token=token)

    async def login(self, data: PartnerLoginRequest):
        partner = await self._get_by(email=data.email)
        # partner = (
        #     await self.session.execute(
        #         select(PartnerModel).where(PartnerModel.email == data.email)
        #     )
        # ).scalar_one_or_none()
        if not partner:
            raise HTTPException(
                status_code=400, detail="partner not found. please try latter"
            )
        verify_partner = verify_password(data.password, partner.password)
        if not verify_partner:
            raise HTTPException(
                status_code=400, detail="partner verify failed. please try latter"
            )

        token = encode_token(
            {"id": str(partner.id), "email": partner.email, "name": partner.name}
        )
        return PartnerLoginResponse(**partner.model_dump(), access_token=token)
