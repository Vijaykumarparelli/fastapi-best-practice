import re
from uuid import UUID

from pydantic import EmailStr, field_validator
from sqlmodel import Field, SQLModel


class PartnerLoginRequest(SQLModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if not re.fullmatch(
            r"(?=.*\d)"
            r"(?=.*[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?~`])"
            r"[A-Z].*[^!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?~`]",
            value,
        ):
            raise ValueError(
                "Password must start with an uppercase letter, "
                "contain a number and a symbol, "
                "and must not end with a symbol"
            )
        if len(value) < 6:
            raise ValueError("Password must be at least 6 characters long")
        return value


class PartnerCreateRequest(PartnerLoginRequest):
    name: str
    zip_codes: list[int]
    max_capacity: int = Field(ge=0, le=5)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        if len(value) < 3:
            raise ValueError("Name atleast 3 chars")
        if len(value) > 25:
            raise ValueError("Name below 25 chars")
        return value

    @field_validator("zip_codes")
    @classmethod
    def validate_zip_codes(cls, value: list[int]):
        if len(set(value)) != len(value):
            raise ValueError("zip_codes cannot contain duplicates")

        for zip_code in value:
            if not 400000 <= zip_code <= 666666:
                raise ValueError(f"Invalid zip code: {zip_code}")

        return value


class PartnerResponse(SQLModel):
    id: UUID
    name: str
    email: str
    max_capacity: int
    zip_codes: list[int]


class PartnerLoginResponse(PartnerResponse):
    access_token: str
