from . import models
from .database import engine, SessionLocal
from db import models, schemas
from util import Period, get_up_to_date
from security import get_password_hash
from .exceptions import AlertNotOwnedError, AlertNotFoundError
from sqlalchemy import and_, or_

models.Base.metadata.create_all(bind=engine)


class Database:
    def __init__(self, session):
        self._session = session

    def get_user_by_username(self, username: str):
        return self._session.query(models.User).filter(models.User.username == username).first()

    def set_user_firebase_token(self, username: str, firebase_token: str):
        user = self._session.query(models.User).filter(models.User.username == username).first()
        user.firebase_token = firebase_token
        self._session.commit()

    def create_user(self, user: schemas.UserCreate):
        db_user = models.User(
            username=user.username,
            hashed_password=get_password_hash(user.password)
        )
        self._session.add(db_user)
        self._session.commit()
        self._session.refresh(db_user)
        return db_user

    def create_alert_for_user(self, alert: schemas.AlertCreate, user_id: int):
        db_alert = models.Alert(**alert.dict(), owner_id=user_id)
        self._session.add(db_alert)
        self._session.commit()
        self._session.refresh(db_alert)
        return db_alert

    def change_alert_state(self, alert_id: int, active: bool, current_user_username: str):
        alert = self._session.query(models.Alert).filter(models.Alert.id == alert_id).first()
        if alert is None:
            raise AlertNotFoundError()
        if alert.owner.username != current_user_username:
            raise AlertNotOwnedError()
        alert.active = active
        self._session.commit()
        return alert

    def delete_alert(self, alert_id: int, current_user_username: str):
        alert = self._session.query(models.Alert).filter(models.Alert.id == alert_id).first()
        if alert is None:
            raise AlertNotFoundError()
        if alert.owner.username != current_user_username:
            raise AlertNotOwnedError()
        self._session.delete(alert)
        self._session.commit()

    def add_sensor_data(self, sensor_data: schemas.SensorDataCreate):
        db_sensor_data = models.SensorData(**sensor_data.dict())
        self._session.add(db_sensor_data)
        self._session.commit()
        self._session.refresh(db_sensor_data)
        return db_sensor_data

    def get_sensor_data(self, period: Period):
        up_to = get_up_to_date(period)
        return self._session.query(models.SensorData).filter(models.SensorData.timestamp > up_to).all()

    def get_alerts_to_trigger(self, temperature: float):
        return self._session.query(models.Alert).filter(
            or_(
                and_(models.Alert.target >= temperature, models.Alert.direction == models.Direction.OVER),
                and_(models.Alert.target <= temperature, models.Alert.direction == models.Direction.UNDER)
            )
        ).all()
