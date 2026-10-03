from uuid import UUID, uuid4

from pydantic import EmailStr
from sqlalchemy import JSON, Column
from sqlmodel import Field, Relationship, SQLModel


class PartnerModel(SQLModel, table=True):
    __tablename__ = "delivery_partners"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    email: EmailStr
    password: str
    zip_codes: list[int] = Field(sa_column=Column(JSON))
    max_capacity: int = Field(ge=0, le=5)
    shipments: list["ShipmentModel"] = Relationship(
        back_populates="partner", sa_relationship_kwargs={"lazy": "selectin"}
    )


from .shipment_model import ShipmentModel
