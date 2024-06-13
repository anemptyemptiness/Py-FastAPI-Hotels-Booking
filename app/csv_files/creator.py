import csv
import json


def create_csv(table_name: str):
    with open(f"{table_name}.csv", "w+", newline='', encoding="utf-8") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            delimiter='\t',
            fieldnames=["id", "hotel_id", "name", "description", "price", "services", "quantity", "image_id"],
        )
        writer.writerow(
            {
                "id": 1,
                "hotel_id": 1,
                "name": "Улучшенный с террасой и видом на озеро",
                "description": "Номер с видом на горы.",
                "price": 24500,
                "services": json.dumps(["Бесплатный Wi‑Fi", "Кондиционер (с климат-контролем)"]),
                "quantity": 5,
                "image_id": 7,
            }
        )


create_csv("rooms")
