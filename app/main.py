import sentry_sdk
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_versioning import VersionedFastAPI
from redis import asyncio as aioredis
# from prometheus_fastapi_instrumentator import Instrumentator
from sqladmin import Admin

from app.admin.auth import authentication_backend
from app.admin.view import BookingsAdmin, HotelsAdmin, RoomsAdmin, UsersAdmin
from app.bookings.router import router as router_bookings
from app.config import settings
from app.database import engine
from app.hotels.rooms.router import router as router_hotels_rooms
from app.hotels.router import router as router_hotels
from app.images.router import router as router_images
from app.pages.router import router as router_pages
from app.users.router import router as router_users
from app.importer.router import router as router_csv


sentry_sdk.init(
    dsn=settings.SENTRY_LINK,
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)


app = FastAPI(
    title="Бронирование отелей",
)

app.include_router(router_users)
app.include_router(router_bookings)
app.include_router(router_hotels)
app.include_router(router_hotels_rooms)
app.include_router(router_pages)
app.include_router(router_images)
app.include_router(router_csv)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    redis = aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}")
    FastAPICache.init(RedisBackend(redis), prefix="cache")
    yield


app = VersionedFastAPI(
    app,
    version_format='{major}',
    prefix_format='/v{major}',
    lifespan=lifespan,
)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# instrumentator = Instrumentator(
#     should_group_status_codes=False,
#     excluded_handlers=[".*admin.*", "/metrics"]
# )
# instrumentator.instrument(app).expose(app)

admin = Admin(app, engine=engine, authentication_backend=authentication_backend)
admin.add_view(UsersAdmin)
admin.add_view(BookingsAdmin)
admin.add_view(HotelsAdmin)
admin.add_view(RoomsAdmin)
