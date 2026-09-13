from decimal import Decimal

from vehicle_service.models import Vehicle, VehicleStatus
from vehicle_service.schemas import VehicleCreate


def test_vehicle_defaults_to_available():
    data = VehicleCreate(brand="Honda", model="Civic", year=2022, color="Black", price="99000.00")
    vehicle = Vehicle(**data.model_dump())
    assert vehicle.status is None or vehicle.status == VehicleStatus.available
    assert vehicle.price == Decimal("99000.00")

