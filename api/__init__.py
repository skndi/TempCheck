import asyncio
from jose import JWTError
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sensor import check_data
from db import schemas, Database
from security import verify_password, get_username_from_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_db():
    db = Database()
    try:
        yield db
    finally:
        pass


async def save_sensor_data(db: Database):
    while True:
        sensor_output = check_data()
        sensor_data_create = schemas.SensorDataCreate(temperature=sensor_output.temperature,
                                                      humidity=sensor_output.humidity)
        db.add_sensor_data(sensor_data=sensor_data_create)
        await asyncio.sleep(300)


def get_current_user(db: Database = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        username = get_username_from_token(token)
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.get_user_by_username(username=username)
    if user is None:
        raise credentials_exception
    return user


def authenticate_user(db: Database, username: str, password: str):
    user = db.get_user_by_username(username=username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
