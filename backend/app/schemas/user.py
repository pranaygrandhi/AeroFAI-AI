from enum import Enum

from pydantic import BaseModel, EmailStr


class UserRole(str, Enum):
    admin = "admin"
    quality_manager = "quality_manager"
    inspector = "inspector"
    engineer = "engineer"
    viewer = "viewer"


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int


class Token(BaseModel):
    access_token: str
    token_type: str
