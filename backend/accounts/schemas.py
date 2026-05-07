from ninja import Schema
from pydantic import EmailStr, Field, model_validator
from typing import Optional, Annotated, Self

# Auth schemas

class RefreshIn(Schema):
    refresh: str

class LoginIn(Schema):
    email: EmailStr
    password: str

class TokenOut(Schema):
    access: str
    refresh: str

class UserOut(Schema):
    id: int
    name: Optional[str] = None
    email: str
    avatar: Optional[str] = None
    is_superuser: bool = False
    role: list[str] = []

    @staticmethod
    def resolve_role(obj):
        return list(obj.groups.values_list('name', flat=True))

class UpdateMeIn(Schema):
    name: Optional[str] = None
    current_password: Optional[str] = None
    new_password: Optional[str] = None

    @model_validator(mode='after')
    def check_password_fields(self) -> Self:
        if self.new_password and not self.current_password:
            raise ValueError('To change your password, inform your actual password')
        return self

# Passwords Reset Schemas

class ForgotPasswordIn(Schema):
    email: EmailStr

class ResetPasswordIn(Schema):
    uid: str
    token: str
    password: Annotated[str, Field(min_length=8)]
    repeat_password: str
