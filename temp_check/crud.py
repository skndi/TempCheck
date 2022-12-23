from sqlalchemy.orm import Session
import datetime

from . import models, schemas
from .period import Period


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "    notreallyhashed"
    db_user = models.User(email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_alerts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Alert).offset(skip).limit(limit).all()


def create_user_alert(db: Session, alert: schemas.AlertCreate, user_id: int):
    db_alert = models.Alert(**alert.dict(), owner_id=user_id)
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert


def add_sensor_data(db: Session, sensor_data: schemas.SensorDataCreate):
    db_sensor_data = models.SensorData(**sensor_data.dict())
    db.add(db_sensor_data)
    db.commit()
    db.refresh(db_sensor_data)
    return db_sensor_data


def get_sensor_data(db: Session, period: Period):
    current_time = datetime.datetime.utcnow()

    if period == Period.DAY:
        up_to = current_time - datetime.timedelta(days=1)
    elif period == Period.WEEK:
        up_to = current_time - datetime.timedelta(weeks=1)
    elif period == Period.MONTH:
        up_to = current_time - datetime.timedelta(days=30)
    elif period == Period.YEAR:
        up_to = current_time - datetime.timedelta(days=365)
    else:
        up_to = None

    return db.query(models.SensorData).filter(models.SensorData.timestamp > up_to).all()
