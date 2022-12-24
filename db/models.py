from sqlalchemy import Column, ForeignKey, Integer, String, Float, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum

from db.database import Base


class Direction(str, Enum):
    OVER = "OVER"
    UNDER = "UNDER"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    alerts = relationship("Alert", back_populates="owner")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    target = Column(Float, index=True)
    direction = Column(String, index=True)
    active = Column(Boolean, index=True, default=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="alerts")


class SensorData(Base):
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, server_default=func.now())
    temperature = Column(Float, index=True)
    humidity = Column(Float, index=True)
