# DATA ACCESS OBJECT
from datetime import date

from sqlalchemy import and_, delete, func, insert, or_, select
from sqlalchemy.exc import SQLAlchemyError

from app.bookings.models import Bookings
from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.exceptions.booking_exceptions import NotCurrentUserToDeleteBookingException
from app.hotels.rooms.models import Rooms
from app.logger import logger


class BookingDAO(BaseDAO):
    model = Bookings

    @classmethod
    async def add(cls, user_id: int, room_id: int, date_from: date, date_to: date):
        async with async_session_maker() as session:
            try:
                booked_rooms = (
                    select(Bookings).where(
                        and_(
                            Bookings.room_id == room_id,
                            or_(
                                and_(
                                    Bookings.date_from >= date_from,
                                    Bookings.date_from <= date_to,
                                ),
                                and_(
                                    Bookings.date_from <= date_from,
                                    Bookings.date_to > date_from,
                                ),
                            ),
                        )
                    )
                ).cte("booked_rooms")

                get_rooms_left = (
                    select(Rooms.quantity - func.count(booked_rooms.c.room_id))
                    .select_from(Rooms)
                    .outerjoin(booked_rooms, booked_rooms.c.room_id == Rooms.id)
                    .where(Rooms.id == room_id)
                    .group_by(Rooms.quantity, booked_rooms.c.room_id)
                )
                rooms_left = await session.execute(get_rooms_left)
                rooms_left: int = rooms_left.scalar()

                if rooms_left > 0:
                    get_price = select(Rooms.price).filter_by(id=room_id)

                    price = await session.execute(get_price)
                    price: int = price.scalar()

                    add_booking = (
                        insert(Bookings)
                        .values(
                            room_id=room_id,
                            user_id=user_id,
                            date_from=date_from,
                            date_to=date_to,
                            price=price,
                        )
                        .returning(Bookings)
                    )

                    new_booking = await session.execute(add_booking)
                    await session.commit()
                    return new_booking.scalar()
                return None
            except (SQLAlchemyError, Exception) as e:
                if isinstance(e, SQLAlchemyError):
                    msg = "Database"
                elif isinstance(e, Exception):
                    msg = "Unknown"
                msg += " Exc: Cannot add booking"

                extra = {
                    "user_id": user_id,
                    "room_id": room_id,
                    "date_from": date_from,
                    "date_to": date_to,
                }

                logger.error(msg, extra=extra, exc_info=True)

    @classmethod
    async def find_all_by_user(
        cls,
        user_id: int,
    ):
        async with async_session_maker() as session:
            query = (
                select(
                    Bookings.room_id,
                    Bookings.user_id,
                    Bookings.date_from,
                    Bookings.date_to,
                    Bookings.price,
                    Bookings.total_cost,
                    Bookings.total_days,
                    Rooms.image_id,
                    Rooms.name,
                    (func.coalesce(Rooms.description, "no description")).label(
                        "description"
                    ),
                    Rooms.services,
                )
                .select_from(Rooms)
                .join(Bookings, Bookings.room_id == Rooms.id, isouter=True)
                .where(Bookings.user_id == user_id)
            )

            result = await session.execute(query)

            return result.mappings().all()

    @classmethod
    async def delete_by_user(
        cls,
        user_id: int,
        booking_id: int,
    ):
        async with async_session_maker() as session:
            query = (
                select(Bookings.user_id)
                .select_from(Bookings)
                .where(Bookings.id == booking_id)
            )

            result = await session.execute(query)
            cur_user_id = result.scalar()

            if cur_user_id != user_id:
                raise NotCurrentUserToDeleteBookingException

            stmt = delete(Bookings).where(Bookings.id == booking_id)

            await session.execute(stmt)
            await session.commit()
