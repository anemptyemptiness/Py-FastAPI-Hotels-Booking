from datetime import datetime

from app.bookings.dao import BookingDAO


async def test_add_and_get_booking():
    new_booking = await BookingDAO.add(
        user_id=2,
        room_id=2,
        date_from=datetime.strptime('2023-07-10', '%Y-%m-%d'),
        date_to=datetime.strptime('2023-07-24', '%Y-%m-%d'),
    )

    assert new_booking.user_id == 2
    assert new_booking.room_id == 2

    new_booking = await BookingDAO.find_by_id(new_booking.id)

    assert new_booking is not None


async def test_crud_booking():
    new_booking = await BookingDAO.add(
        user_id=1,
        room_id=4,
        date_from=datetime.strptime("2024-09-06", "%Y-%m-%d"),
        date_to=datetime.strptime("2024-09-21", "%Y-%m-%d"),
    )
    assert new_booking == 4

    new_booking = await BookingDAO.find_one_or_none(id=4)
    assert new_booking.id == 4

    await BookingDAO.delete_by_user(
        user_id=1,
        booking_id=4,
    )
    bookings = await BookingDAO.find_all(user_id=1)
    assert len(bookings) == 2
