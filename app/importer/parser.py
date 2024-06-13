import codecs
import copy
import csv
import json
from datetime import datetime

from fastapi import UploadFile

from app.exceptions.csv_parser_exceptions import WrongTableNameException


def parse_csv_to_list_of_dicts(
        table_name: str,
        file: UploadFile,
) -> dict:
    data: dict = dict()

    if table_name == "hotels":
        fieldnames = ["id", "name", "location", "services", "rooms_quantity", "image_id"]
    elif table_name == "rooms":
        fieldnames = ["id", "hotel_id", "name", "description", "price", "services", "quantity", "image_id"]
    else:
        raise WrongTableNameException

    csv_reader = csv.DictReader(
        codecs.iterdecode(file.file, encoding="utf-8"),
        dialect=csv.excel_tab,
        fieldnames=fieldnames,
    )

    for row in csv_reader:
        if table_name == "hotels":
            row["id"] = int(row["id"])
            row["rooms_quantity"] = int(row["rooms_quantity"])
            row["image_id"] = int(row["image_id"])
            row["services"] = json.loads(row["services"])
        elif table_name == "rooms":
            row["id"] = int(row["id"])
            row["hotel_id"] = int(row["hotel_id"])
            row["price"] = int(row["price"])
            row["quantity"] = int(row["quantity"])
            row["image_id"] = int(row["image_id"])
            row["services"] = json.loads(row["services"])

        data = row

    file.file.close()
    return data

