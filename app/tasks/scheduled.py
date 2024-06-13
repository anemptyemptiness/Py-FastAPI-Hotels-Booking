import asyncio
from datetime import datetime, timedelta, timezone
import smtplib

from pydantic import EmailStr

from app.tasks.celery_app import celery_app
from app.tasks.email_templates import (
    create_booking_notification_tomorrow_template,
    create_booking_notification_per_3_days_template,
)
from app.config import settings
from app.bookings.dao import BookingDAO
from app.users.dao import UsersDAO


async def get_bookings():
    return await BookingDAO.find_all()


async def get_user(user_id: int):
    return await UsersDAO.find_by_id(model_id=user_id)


@celery_app.task(name="notification_for_tomorrow")
def send_notification_of_booking_for_tomorrow():
    bookings = asyncio.run(get_bookings())

    for booking in bookings:
        user = asyncio.run(get_user(user_id=booking["user_id"]))

        if (booking["date_from"] - datetime.now(tz=timezone(timedelta(hours=3))).date()).days == 1:
            msg_content = create_booking_notification_tomorrow_template(booking=booking, email_to=user["email"])

            with smtplib.SMTP_SSL(host=settings.SMTP_HOST, port=settings.SMTP_PORT) as server:
                server.login(user=settings.SMTP_USER, password=settings.SMTP_PASS)
                server.send_message(msg_content)


@celery_app.task(name="notification_per_3_days")
def send_notification_of_booking_per_3_days():
    bookings = asyncio.run(get_bookings())

    for booking in bookings:
        user = asyncio.run(get_user(user_id=booking["user_id"]))

        if (booking["date_from"] - datetime.now(tz=timezone(timedelta(hours=3))).date()).days == 3:
            msg_content = create_booking_notification_per_3_days_template(booking=booking, email_to=user["email"])

            with smtplib.SMTP_SSL(host=settings.SMTP_HOST, port=settings.SMTP_PORT) as server:
                server.login(user=settings.SMTP_USER, password=settings.SMTP_PASS)
                server.send_message(msg_content)
