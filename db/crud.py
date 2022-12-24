from sqlalchemy.orm import Session

from db import models
from api import schemas
from util import Period, get_up_to_date
from security import get_password_hash
from .exceptions import AlertNotOwnedError, AlertNotFoundError


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        username=user.username,
        hashed_password=get_password_hash(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_alert_for_user(db: Session, alert: schemas.AlertCreate, user_id: int):
    db_alert = models.Alert(**alert.dict(), owner_id=user_id)
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert


def change_alert_state(db: Session, alert_id: int, active: bool, current_user_username: str):
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if alert is None:
        raise AlertNotFoundError()
    if alert.owner.username != current_user_username:
        raise AlertNotOwnedError()
    alert.active = active
    db.commit()
    return alert


def delete_alert(db: Session, alert_id: int, current_user_username: str):
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if alert is None:
        raise AlertNotFoundError()
    if alert.owner.username != current_user_username:
        raise AlertNotOwnedError()
    db.delete(alert)
    db.commit()


def add_sensor_data(db: Session, sensor_data: schemas.SensorDataCreate):
    db_sensor_data = models.SensorData(**sensor_data.dict())
    db.add(db_sensor_data)
    db.commit()
    db.refresh(db_sensor_data)
    return db_sensor_data


def get_sensor_data(db: Session, period: Period):
    up_to = get_up_to_date(period)
    return db.query(models.SensorData).filter(models.SensorData.timestamp > up_to).all()
