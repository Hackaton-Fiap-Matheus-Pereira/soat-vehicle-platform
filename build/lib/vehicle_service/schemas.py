from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from .models import VehicleStatus


class VehicleCreate(BaseModel):
    brand: str = Field(min_length=1, max_length=80)
    model: str = Field(min_length=1, max_length=120)
    year: int = Field(ge=1886, le=2100)
    color: str = Field(min_length=1, max_length=50)
    price: Decimal = Field(gt=0, decimal_places=2, max_digits=12)


class VehicleUpdate(BaseModel):
    brand: str | None = Field(default=None, min_length=1, max_length=80)
    model: str | None = Field(default=None, min_length=1, max_length=120)
    year: int | None = Field(default=None, ge=1886, le=2100)
    color: str | None = Field(default=None, min_length=1, max_length=50)
    price: Decimal | None = Field(default=None, gt=0, decimal_places=2, max_digits=12)


class VehicleResponse(BaseModel):
    id: str
    brand: str
    model: str
    year: int
    color: str
    price: Decimal
    status: VehicleStatus
    model_config = ConfigDict(from_attributes=True)


class SaleResponse(BaseModel):
    id: str
    buyer_id: str
    sale_price: Decimal
    sold_at: datetime
    vehicle: VehicleResponse
    model_config = ConfigDict(from_attributes=True)

