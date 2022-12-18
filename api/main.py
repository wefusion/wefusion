import json

import aio_pika
import neo4j
from aio_pika.abc import AbstractRobustConnection
from aio_pika.channel import Channel
from aio_pika.pool import Pool
from fastapi import FastAPI
from pydantic.json import pydantic_encoder
from sqlalchemy.ext.asyncio import create_async_engine

from api.core import connection_store, settings
from api.routes import api_router

app = FastAPI(
    title="Wefusion API", openapi_url="/api/openapi.json", docs_url="/api/docs"
)


def json_serializer(*args, **kwargs) -> str:
    return json.dumps(*args, default=pydantic_encoder, **kwargs)


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

    connection_store.sqla_engine = create_async_engine(
        settings.POSTGRES_DSN, json_serializer=json_serializer
    )

    connection_store.neo4j_driver = neo4j.AsyncGraphDatabase().driver(
        settings.NEO4J_URI, auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
    )


app.include_router(api_router, prefix="/api")
