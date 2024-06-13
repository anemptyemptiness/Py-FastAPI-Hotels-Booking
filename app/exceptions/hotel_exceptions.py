from fastapi import HTTPException, status


class HotelException(HTTPException):
    status_code = 500
    detail = ""

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class DateFromCannotBeGreaterOrEqualThanDateToException(HotelException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Дата въезда не может быть позже даты выезда"


class RentingDateIsTooLongException(HotelException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Срок аренды комнаты слишком большой"
