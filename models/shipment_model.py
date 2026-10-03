from datetime import datetime, timedelta, timezone
from enum import Enum
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel


class ShipmentStatus(str, Enum):
    placed = "placed"
    in_transit = "in_transit"
    out_of_delivery = "out_of_delivery"
    delivered = "delivered"


class ShipmentModel(SQLModel, table=True):
    __tablename__ = "shipment"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    content: str
    weight: float = Field(le=25)
    destination: int
    status: ShipmentStatus
    estimated_delivery: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc) + timedelta(days=5)
    )
    user_id: UUID = Field(foreign_key="users.id")
    partner_id: UUID | None = Field(default=None, foreign_key="delivery_partners.id")

    user: "UserModel" = Relationship(
        back_populates="shipment", sa_relationship_kwargs={"lazy": "selectin"}
    )
    partner: "PartnerModel" = Relationship(
        back_populates="shipments", sa_relationship_kwargs={"lazy": "selectin"}
    )


from .auth_model import UserModel
from .partner_model import PartnerModel
