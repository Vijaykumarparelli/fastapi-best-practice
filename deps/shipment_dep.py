from typing import Annotated

from fastapi import Depends

from config.db import DBSession
from controllers.shipment_controller import ShipmentController


def init_shipment_controller(session: DBSession):
    return ShipmentController(session)


ShipmentControllerDep = Annotated[ShipmentController, Depends(init_shipment_controller)]
