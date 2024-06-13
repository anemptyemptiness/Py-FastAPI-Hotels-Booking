import pytest
from httpx import AsyncClient


@pytest.mark.parametrize(
    "location, date_from, date_to, status_code", [
        ("Республика Алтай, Майминский район, село Урлу-Аспак, Лесхозная улица, 20", "2024-06-09", "2024-06-25", 200),
        ("Республика Алтай, Майминский район, село Урлу-Аспак, Лесхозная улица, 20", "2024-06-09", "2024-06-09", 400),
        ("Республика Алтай, Майминский район, село Урлу-Аспак, Лесхозная улица, 20", "2024-07-09", "2024-06-25", 400),
        ("Республика Алтай, Майминский район, село Урлу-Аспак, Лесхозная улица, 20", "2024-06-09", "2024-07-25", 400),
    ]
)
async def test_get_hotels(location, date_from, date_to, status_code, ac: AsyncClient):
    response = await ac.get("/hotels", params={
        "location": location,
        "date_from": date_from,
        "date_to": date_to,
    })

    assert response.status_code == status_code
