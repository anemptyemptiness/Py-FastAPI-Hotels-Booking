from datetime import date

from sqlalchemy import and_, func, select

from app.bookings.models import Bookings
from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.hotels.models import Hotels
from app.hotels.rooms.models import Rooms


class HotelsDAO(BaseDAO):
    model = Hotels

    @classmethod
    async def find_all_available(
            cls,
            location: str,
            date_from: date,
            date_to: date,
    ):
        async with async_session_maker() as session:
            booked_rooms = (
                select(Bookings.room_id, (func.count(Bookings.room_id)).label("total_blocked"))
                .select_from(Bookings)
                .where(
                    and_(Bookings.date_from > date_from, Bookings.date_to < date_to)
                )
                .group_by(Bookings.room_id)
            ).cte("booked_rooms")

            rooms_left = (
                select(
                    Rooms.hotel_id,
                    Rooms.id,
                    (Hotels.rooms_quantity - booked_rooms.c.total_blocked).label("available_rooms"),
                )
                .select_from(Rooms)
                .join(booked_rooms, booked_rooms.c.room_id == Rooms.id)
                .join(Hotels, Hotels.id == Rooms.hotel_id)
                .where((Hotels.rooms_quantity - booked_rooms.c.total_blocked) > 0)
            ).cte("rooms_left")

            query = (
                select(
                    Hotels.id,
                    Hotels.name,
                    Hotels.location,
                    Hotels.services,
                    Hotels.rooms_quantity,
                    Hotels.image_id,
                    (func.coalesce(rooms_left.c.available_rooms, Hotels.rooms_quantity)).label("rooms_left")
                )
                .select_from(Hotels)
                .join(rooms_left, rooms_left.c.hotel_id == Hotels.id, isouter=True)
                .where(Hotels.location.like(f'%{location}%'))
            )
            result = await session.execute(query)

            return result.mappings().all()
