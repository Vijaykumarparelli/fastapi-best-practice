from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel


class UserModel(SQLModel, table=True):
    __tablename__ = "users"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    email: str
    password: str
    shipment: list["ShipmentModel"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )


from .shipment_model import ShipmentModel
