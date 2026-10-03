import re
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr, field_validator
from sqlmodel import SQLModel


class UserLoginRequest(SQLModel):
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


class UserCreateRequest(UserLoginRequest):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        if len(value) < 3:
            raise ValueError("Name atleast 3 chars")
        if len(value) > 25:
            raise ValueError("Name below 25 chars")
        return value


class UserResponse(SQLModel):
    id: UUID
    name: str
    email: str


class UserLoginResponse(UserResponse):
    access_token: str


UserLoginFormData = Annotated[OAuth2PasswordRequestForm, Depends()]
