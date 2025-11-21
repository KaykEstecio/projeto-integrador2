from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import database, models, schemas
from .auth import get_current_user

router = APIRouter(
    prefix="/vehicles",
    tags=["vehicles"]
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.Vehicle)
def create_vehicle(vehicle: schemas.VehicleCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_vehicle = models.Vehicle(**vehicle.dict(), owner_id=current_user.id)
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle

@router.get("/", response_model=List[schemas.Vehicle])
def read_vehicles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    vehicles = db.query(models.Vehicle).offset(skip).limit(limit).all()
    return vehicles

@router.get("/my-vehicles", response_model=List[schemas.Vehicle])
def read_my_vehicles(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return current_user.vehicles

@router.delete("/{vehicle_id}")
def delete_vehicle(vehicle_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    if vehicle.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this vehicle")
    db.delete(vehicle)
    db.commit()
    return {"detail": "Vehicle deleted"}

@router.put("/{vehicle_id}", response_model=schemas.Vehicle)
def update_vehicle(vehicle_id: int, vehicle_update: schemas.VehicleCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    if vehicle.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this vehicle")
    
    for key, value in vehicle_update.dict().items():
        setattr(vehicle, key, value)
    
    db.commit()
    db.refresh(vehicle)
    return vehicle
