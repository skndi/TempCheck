from pydantic import BaseModel
from datetime import datetime
from typing import Union


class AlertBase(BaseModel):
    target: float


class AlertCreate(AlertBase):
    pass


class Alert(AlertBase):
    id: int

    class Config:
        orm_mode = True


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


class TokenData(BaseModel):
    username: Union[str, None] = None