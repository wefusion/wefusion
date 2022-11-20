import aio_pika
from aio_pika.abc import AbstractRobustConnection
from aio_pika.channel import Channel
from aio_pika.pool import Pool
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine

from api.core import connection_store, settings
from api.routes import execution

app = FastAPI(title="Wefusion API")


@app.on_event("startup")
async def startup():
    async def get_connection() -> AbstractRobustConnection:
        return await aio_pika.connect_robust(settings.RABBITMQ_DSN)

    connection_pool: Pool = Pool(get_connection, max_size=1)

    async def get_channel() -> Channel:
        async with connection_pool.acquire() as connection:
            return await connection.channel()

    channel_pool: Pool = Pool(get_channel, max_size=10)

    connection_store.rbmq_channel_pool = channel_pool
    connection_store.sqla_engine = create_async_engine(settings.POSTGRES_DSN)


app.include_router(execution.router, prefix="/exec", tags=["Task execution"])
