from datetime import date
from typing import Annotated

from fastapi import APIRouter, Path

from app.hotels.rooms.dao import RoomsDAO
from app.hotels.rooms.schemas import SRooms

router = APIRouter(
    prefix="/hotels",
    tags=["Комнаты"]
)


@router.get("/{hotel_id}/rooms")
async def get_rooms(
        hotel_id: Annotated[int, Path()],
        date_from: date,
        date_to: date,
) -> list[SRooms]:
    data = await RoomsDAO.get_rooms(
        hotel_id=hotel_id,
        date_from=date_from,
        date_to=date_to,
    )

    return data
