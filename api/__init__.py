from db.database import SessionLocal
from sqlalchemy.orm import Session
from sensor import check_data
from db import crud
from api import schemas
import asyncio
from jose import JWTError
from security import verify_password, get_username_from_token
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def save_sensor_data(db: Session):
    while True:
        sensor_output = check_data()
        sensor_data_create = schemas.SensorDataCreate(temperature=sensor_output.temperature,
                                                      humidity=sensor_output.humidity)
        crud.add_sensor_data(db=db, sensor_data=sensor_data_create)
        await asyncio.sleep(300)


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        username = get_username_from_token(token)
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


def authenticate_user(db: Session, username: str, password: str):
    user = crud.get_user_by_username(db, username=username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
