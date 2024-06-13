from fastapi import HTTPException, status


class CsvFilesParserException(HTTPException):
    status_code = 500
    detail = ""

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class WrongTableNameException(CsvFilesParserException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Вы ввели некорректное имя таблицы для вставки данных"