from fastapi import Depends, FastAPI, HTTPException, Response
from sqlalchemy.orm import Session
import asyncio

from db import models, crud, schemas
from util import Period
from db.database import SessionLocal, engine
from sensor import check_data, SensorOutput
from plot import get_image_bytes

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


async def save_sensor_data(db: Session):
    while True:
        sensor_output = check_data()
        sensor_data_create = schemas.SensorDataCreate(temperature=sensor_output.temperature,
                                                      humidity=sensor_output.humidity)
        crud.add_sensor_data(db=db, sensor_data=sensor_data_create)
        await asyncio.sleep(300)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event('startup')
async def app_startup():
    db = next(get_db())
    asyncio.create_task(save_sensor_data(db=db))


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=list[schemas.User])
def read_users(db: Session = Depends(get_db)):
    users = crud.get_users(db)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/{user_id}/alerts/", response_model=schemas.Alert)
def create_alert_for_user(
        user_id: int, alert: schemas.AlertCreate, db: Session = Depends(get_db)
):
    return crud.create_user_alert(db=db, alert=alert, user_id=user_id)


@app.get("/alerts/", response_model=list[schemas.Alert])
def read_alerts(db: Session = Depends(get_db)):
    alerts = crud.get_alerts(db)
    return alerts


@app.get("/history/", response_model=list[schemas.SensorData])
def read_sensor_data_history(period: Period, db: Session = Depends(get_db)):
    sensor_data = crud.get_sensor_data(db, period=period)
    return sensor_data


@app.get(
    "/history/image",
    responses={
        200: {
            "content": {"image/png": {}}
        }
    },
    response_class=Response,
)
def get_sensor_data_history_plot(period: Period):
    image_bytes = get_image_bytes(period=period)
    return Response(content=image_bytes, media_type="image/png")


@app.get("/current/", response_model=SensorOutput)
def get_current_sensor_data():
    return check_data()
