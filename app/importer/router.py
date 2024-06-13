from fastapi import APIRouter, Query, UploadFile, Depends

from app.exceptions.csv_parser_exceptions import WrongTableNameException
from app.importer.parser import parse_csv_to_list_of_dicts
from app.users.dependencies import get_current_user
from app.users.models import Users
from app.hotels.dao import HotelsDAO
from app.hotels.rooms.dao import RoomsDAO

from typing import Annotated


router = APIRouter(
    prefix="/import",
    tags=["Загрузка данных в БД"],
)


@router.post("", status_code=201)
async def get_data_to_table(
        table_name: Annotated[str, Query()],
        file: UploadFile,
        user: Users = Depends(get_current_user)
) -> None:
    data = parse_csv_to_list_of_dicts(table_name=table_name, file=file)

    if table_name == "hotels":
        await HotelsDAO.add(**data)
    elif table_name == "rooms":
        await RoomsDAO.add(**data)
    else:
        raise WrongTableNameException
