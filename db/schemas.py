from pydantic import BaseModel
from datetime import datetime
from typing import Union
from db.models import Direction


class AlertBase(BaseModel):
    target: float
    direction: Direction


class AlertCreate(AlertBase):
    pass


class Alert(AlertBase):
    id: int
    active: bool

    class Config:
        orm_mode = True


class AlertChangeState(BaseModel):
    active: bool


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    alerts: list[Alert] = []

    class Config:
        orm_mode = True


class SensorDataBase(BaseModel):
    temperature: float
    humidity: float


class SensorDataCreate(SensorDataBase):
    pass


class SensorData(SensorDataBase):
    timestamp: datetime

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str
