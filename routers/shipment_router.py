from fastapi import APIRouter

from config.security import GetUserFromToken
from deps.shipment_dep import ShipmentControllerDep
from schema.shipment_schema import ShipmentCreate, ShipmentResponse

router = APIRouter(prefix="/shipment", tags=["shipment"])


@router.post("/create", response_model=ShipmentResponse)
async def create_shipment(
    data: ShipmentCreate, user: GetUserFromToken, ctrl: ShipmentControllerDep
):
    return await ctrl.create(data, user)


@router.get("/", response_model=list[ShipmentResponse])
async def get_user_shipments(user: GetUserFromToken, ctrl: ShipmentControllerDep):
    return await ctrl.get_shipment(user)
