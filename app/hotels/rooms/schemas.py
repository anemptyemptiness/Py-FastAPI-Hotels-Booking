from pydantic import BaseModel


class SRooms(BaseModel):
    id: int
    hotel_id: int
    name: str
    description: str
    price: float
    services: list
    quantity: int
    image_id: int
    total_cost: float
    rooms_left: int
