from datetime import date
from typing import Annotated

from fastapi import APIRouter, Path, Query
from fastapi_cache.decorator import cache

from pydantic import TypeAdapter

from app.exceptions.hotel_exceptions import (
    DateFromCannotBeGreaterOrEqualThanDateToException,
    RentingDateIsTooLongException,
)
from app.hotels.dao import HotelsDAO
from app.hotels.schemas import SHotels, SHotelsWithAvailableRooms

router = APIRouter(
    prefix="/hotels",
    tags=["Отели"],
)


@router.get("")
@cache(expire=20)
async def get_hotels(
        location: Annotated[str, Query()],
        date_from: Annotated[date, Query()],
        date_to: Annotated[date, Query()],
):
    hotels = await HotelsDAO.find_all_available(
        date_from=date_from,
        date_to=date_to,
        location=location,
    )

    if date_from >= date_to:
        raise DateFromCannotBeGreaterOrEqualThanDateToException
    if (date_to - date_from).days > 30:
        raise RentingDateIsTooLongException

    hotels_json = TypeAdapter(list[SHotelsWithAvailableRooms]).validate_python(hotels)
    return hotels_json


@router.get("/id/{hotel_id}")
async def get_hotel_by_id(
        hotel_id: Annotated[int, Path()],
) -> list[SHotels]:
    return await HotelsDAO.find_all(id=hotel_id)
