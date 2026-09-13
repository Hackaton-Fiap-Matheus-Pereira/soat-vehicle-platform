from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .database import get_db
from .models import Sale, Vehicle, VehicleStatus
from .schemas import SaleResponse, VehicleCreate, VehicleResponse, VehicleUpdate
from .security import Principal, admin_only, current_user

app = FastAPI(title="SOAT Vehicle Sales Service", version="1.0.0")


@app.get("/health", tags=["Operations"])
async def health():
    return {"status": "ok"}


@app.post("/vehicles", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
async def create_vehicle(data: VehicleCreate, _: Principal = Depends(admin_only), db: AsyncSession = Depends(get_db)):
    vehicle = Vehicle(**data.model_dump())
    db.add(vehicle)
    await db.commit()
    await db.refresh(vehicle)
    return vehicle


@app.patch("/vehicles/{vehicle_id}", response_model=VehicleResponse)
async def update_vehicle(vehicle_id: str, data: VehicleUpdate, _: Principal = Depends(admin_only), db: AsyncSession = Depends(get_db)):
    vehicle = await db.get(Vehicle, vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    if vehicle.status == VehicleStatus.sold:
        raise HTTPException(status_code=409, detail="Sold vehicles cannot be edited")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(vehicle, field, value)
    await db.commit()
    await db.refresh(vehicle)
    return vehicle


@app.get("/vehicles/available", response_model=list[VehicleResponse])
async def available_vehicles(limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0), db: AsyncSession = Depends(get_db)):
    query = select(Vehicle).where(Vehicle.status == VehicleStatus.available).order_by(Vehicle.price, Vehicle.id).limit(limit).offset(offset)
    return list((await db.scalars(query)).all())


@app.get("/vehicles/sold", response_model=list[SaleResponse])
async def sold_vehicles(limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0), _: Principal = Depends(admin_only), db: AsyncSession = Depends(get_db)):
    query = select(Sale).options(selectinload(Sale.vehicle)).order_by(Sale.sale_price, Sale.id).limit(limit).offset(offset)
    return list((await db.scalars(query)).all())


@app.post("/vehicles/{vehicle_id}/purchase", response_model=SaleResponse, status_code=status.HTTP_201_CREATED)
async def purchase(vehicle_id: str, buyer: Principal = Depends(current_user), db: AsyncSession = Depends(get_db)):
    vehicle = await db.scalar(select(Vehicle).where(Vehicle.id == vehicle_id).with_for_update())
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    if vehicle.status != VehicleStatus.available:
        raise HTTPException(status_code=409, detail="Vehicle is no longer available")
    vehicle.status = VehicleStatus.sold
    sale = Sale(vehicle=vehicle, buyer_id=buyer.user_id, sale_price=vehicle.price)
    db.add(sale)
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Vehicle is no longer available") from exc
    return await db.scalar(select(Sale).options(selectinload(Sale.vehicle)).where(Sale.id == sale.id))

