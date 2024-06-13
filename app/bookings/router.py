from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Path
from fastapi_versioning import version
from pydantic import TypeAdapter

from app.bookings.dao import BookingDAO
from app.bookings.schemas import SBooking, SBookingsByUser
from app.exceptions.booking_exceptions import RoomCannotBeBookedException
from app.users.dependencies import get_current_user
from app.users.models import Users
from app.tasks.scheduled import (
    send_notification_of_booking_for_tomorrow,
    send_notification_of_booking_per_3_days,
)

router = APIRouter(
    prefix="/bookings",
    tags=["Бронирования"],
)


@router.get("")
async def get_bookings_by_user(user: Users = Depends(get_current_user)) -> list[SBookingsByUser]:
    return await BookingDAO.find_all_by_user(user_id=user.id)


@router.post("")
@version(1)
async def add_booking(
        room_id: int, date_from: date, date_to: date,
        user: Users = Depends(get_current_user),
):
    booking = await BookingDAO.add(
        user_id=user.id,
        room_id=room_id,
        date_from=date_from,
        date_to=date_to
    )

    if not booking:
        raise RoomCannotBeBookedException

    booking_dict = TypeAdapter(SBooking).dump_python(booking)
    return TypeAdapter(SBooking).validate_python(booking_dict)


@router.delete("/{booking_id}", status_code=204)
@version(1)
async def delete_booking_by_user(
        booking_id: Annotated[int, Path()],
        user: Users = Depends(get_current_user),
) -> None:
    await BookingDAO.delete_by_user(
        user_id=user.id,
        booking_id=booking_id,
    )