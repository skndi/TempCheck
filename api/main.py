from fastapi import Depends, FastAPI, HTTPException, Response, status
from sqlalchemy.orm import Session
import asyncio
from fastapi.security import OAuth2PasswordRequestForm

from db import models, crud
from db.exceptions import AlertNotOwnedError
from util import Period
from sensor import check_data, SensorOutput
from plot import get_image_bytes
from security import create_access_token
from . import get_db, save_sensor_data, authenticate_user, get_current_user, schemas

app = FastAPI()


@app.on_event('startup')
async def app_startup():
    db = next(get_db())
    asyncio.create_task(save_sensor_data(db=db))


@app.post("/register", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)


@app.post("/alerts", response_model=schemas.Alert)
def create_alert_for_current_user(
        alert: schemas.AlertCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    return crud.create_alert_for_user(db=db, alert=alert, user_id=current_user.id)


@app.get("/alerts", response_model=list[schemas.Alert])
def read_alerts_for_current_user(current_user: models.User = Depends(get_current_user)):
    return current_user.alerts


@app.patch("/alerts/{alert_id}", response_model=schemas.Alert)
def change_alert_state(
        alert_id: int,
        alert_change_state: schemas.AlertChangeState,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    try:
        return crud.change_alert_state(
            db=db,
            alert_id=alert_id,
            active=alert_change_state.active,
            current_user_username=current_user.username
        )
    except AlertNotOwnedError:
        raise HTTPException(status_code=403, detail="This alert is not owned by the current user")


@app.delete("/alerts/{alert_id}")
def delete_alert(
        alert_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    try:
        crud.delete_alert(
            db=db,
            alert_id=alert_id,
            current_user_username=current_user.username
        )
    except AlertNotOwnedError:
        raise HTTPException(status_code=403, detail="This alert is not owned by the current user")
    return {"ok": True}


@app.get("/history", response_model=list[schemas.SensorData])
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


@app.post("/login", response_model=schemas.Token)
def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(user.username)
    return {"access_token": access_token, "token_type": "bearer"}
