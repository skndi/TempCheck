from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine
from .period import Period

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
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
def read_alerts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    alerts = crud.get_alerts(db, skip=skip, limit=limit)
    return alerts


@app.post("/temperatures/", response_model=schemas.Temperature)
def add_temperature(
        temperature: schemas.TemperatureCreate, db: Session = Depends(get_db)
):
    return crud.add_temperature(db=db, temperature=temperature)


@app.get("/temperatures/", response_model=list[schemas.Temperature])
def get_temperatures(period: Period, db: Session = Depends(get_db)):
    temperatures = crud.get_temperatures(db, period=period)
    return temperatures
