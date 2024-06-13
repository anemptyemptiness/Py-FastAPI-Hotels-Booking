from datetime import datetime

import pytest


@pytest.mark.parametrize(
    "room_id, date_from, date_to, booked_rooms, status_code", [
        *[(4, '2030-05-01', '2030-05-15', i, 200) for i in range(3, 11)],
        *[(4, '2030-05-01', '2030-05-15', 10, 409)] * 2,
    ]
)
async def test_add_booking(room_id, date_from, date_to, status_code, booked_rooms, authenticated_ac):
    response = await authenticated_ac.post("/bookings", params={
        "room_id": room_id,
        "date_from": datetime.strptime(date_from, "%Y-%m-%d"),
        "date_to": datetime.strptime(date_to, "%Y-%m-%d"),
    })

    assert response.status_code == status_code

    response = await authenticated_ac.get("/bookings")

    assert len(response.json()) == booked_rooms


async def test_get_then_delete_and_then_get_again_booking_by_user(authenticated_ac):
    response = await authenticated_ac.get("/bookings")
    bookings = response.json()
    assert len(bookings) == 2
    assert response.status_code == 200

    booking_id = 1
    response = await authenticated_ac.delete(f"/bookings/{booking_id}")
    assert response.status_code == 204

    booking_id = 2
    response = await authenticated_ac.delete(f"/bookings/{booking_id}")
    assert response.status_code == 204

    response = await authenticated_ac.get("/bookings")
    assert not response.json()

    response = await authenticated_ac.delete(f"/bookings/{booking_id}")
    assert response.status_code == 403
