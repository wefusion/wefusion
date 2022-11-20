from dataclasses import dataclass

from aio_pika import Channel
from aio_pika.pool import Pool
from sqlalchemy.ext.asyncio import AsyncEngine

from core.utils.settings import PostgresSettings, RabbitMQSettings


class Settings(PostgresSettings, RabbitMQSettings):
    pass


settings = Settings()


@dataclass
class ConnectionStore:
    sqla_engine: AsyncEngine = None
    rbmq_channel_pool: Pool[Channel] = None


connection_store = ConnectionStore()
