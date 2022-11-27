from dataclasses import dataclass

from aio_pika import Channel
from aio_pika.pool import Pool
from neo4j import AsyncDriver
from sqlalchemy.ext.asyncio import AsyncEngine

from core.utils.settings import Neo4jSettings, PostgresSettings, RabbitMQSettings


class Settings(PostgresSettings, RabbitMQSettings, Neo4jSettings):
    pass


settings = Settings()


@dataclass
class ConnectionStore:
    sqla_engine: AsyncEngine = None
    neo4j_driver: AsyncDriver = None
    rbmq_channel_pool: Pool[Channel] = None


connection_store = ConnectionStore()
