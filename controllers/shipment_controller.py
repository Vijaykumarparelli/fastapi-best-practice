from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from config.security import GetUserFromToken
from controllers.base_controller import BaseController
from models.shipment_model import ShipmentModel
from schema.shipment_schema import ShipmentCreate


class ShipmentController(BaseController):
    def __init__(self, session: AsyncSession):
        super().__init__(session, ShipmentModel)

    async def create(self, data: ShipmentCreate, user: GetUserFromToken):
        shipment_item = ShipmentModel(**data.model_dump(), user_id=user.id)
        shipment_item = await self._add(shipment_item)
        # self.session.add(shipment_item)
        # await self.session.commit()
        # await self.session.refresh(shipment_item)
        return shipment_item

    async def get_shipment(self, user: GetUserFromToken):
        items = await self._get_all(user_id=user.id)
        # items = (
        #     (
        #         await self.session.execute(
        #             select(ShipmentModel).where(ShipmentModel.user_id == user.id)
        #         )
        #     )
        #     .scalars()
        #     .all()
        # )
        return items
