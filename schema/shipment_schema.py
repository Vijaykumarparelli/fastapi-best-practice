from datetime import datetime
from uuid import UUID

from pydantic import field_validator
from sqlmodel import Field, SQLModel

from models.shipment_model import ShipmentStatus
from schema.auth_schema import UserResponse


class ShipmentCreate(SQLModel):
    content: str
    weight: float = Field(le=25)
    destination: int
    status: ShipmentStatus

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        if len(value) < 5:
            raise ValueError("Content atleast 5 letters")
        return value

    @field_validator("destination")
    @classmethod
    def validate_destination(cls, value: int) -> int:
        if not 400000 <= value <= 666666:
            raise ValueError(
                f"destination Invalid it must between 400000 to 666666: {value}"
            )
        return value


class ShipmentResponse(SQLModel):
    id: UUID
    content: str
    weight: float
    destination: int
    status: ShipmentStatus
    user_id: UUID
    user: UserResponse
    estimated_delivery: datetime
