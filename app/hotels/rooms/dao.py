from datetime import date

from sqlalchemy import Integer, and_, func, select

from app.bookings.models import Bookings
from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.hotels.rooms.models import Rooms


class RoomsDAO(BaseDAO):
    model = Rooms

    @classmethod
    async def get_rooms(
            cls,
            hotel_id: int,
            date_from: date,
            date_to: date,
    ):
        async with async_session_maker() as session:
            booked_rooms = (
                select(
                    Bookings.room_id,
                    func.count(Bookings.room_id).label("total_booked"),
                )
                .select_from(Bookings)
                .where(
                    and_(
                        Bookings.date_from > date_from,
                        Bookings.date_to < date_to,
                    )
                )
                .group_by(Bookings.room_id)
            ).cte("booked_rooms")

            query = (
                select(
                    Rooms.id,
                    Rooms.hotel_id,
                    Rooms.name,
                    Rooms.description,
                    Rooms.services,
                    Rooms.price,
                    Rooms.quantity,
                    Rooms.image_id,
                    func.extract('day', (date_to - date_from) * Rooms.price).label("total_cost"),
                    func.coalesce(Rooms.quantity - booked_rooms.c.total_booked, Rooms.quantity).label("rooms_left")
                )
                .select_from(Rooms)
                .join(booked_rooms, Rooms.id == booked_rooms.c.room_id, isouter=True)
                .where(Rooms.hotel_id == hotel_id)
            )

            result = await session.execute(query)

            return result.mappings().all()
