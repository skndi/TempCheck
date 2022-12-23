from pydantic import BaseModel
from datetime import datetime


class AlertBase(BaseModel):
    target: float


class AlertCreate(AlertBase):
    pass


class Alert(AlertBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    alerts: list[Alert] = []

    class Config:
        orm_mode = True


class TemperatureBase(BaseModel):
    temperature: float


class TemperatureCreate(TemperatureBase):
    pass


class Temperature(TemperatureBase):
    timestamp: datetime

    class Config:
        orm_mode = True
