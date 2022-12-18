from dataclasses import dataclass

from aio_pika import Channel
from aio_pika.pool import Pool
from neo4j import AsyncDriver
from pydantic import Field
from sqlalchemy.ext.asyncio import AsyncEngine

from core.utils.settings import Neo4jSettings, PostgresSettings, RabbitMQSettings


class Settings(PostgresSettings, RabbitMQSettings, Neo4jSettings):
    SECRET_KEY: str = Field(..., env="API_SECRET_KEY")
    SERVICE_KEY: str = Field(..., env="API_SERVICE_KEY")


settings = Settings()


@dataclass
class ConnectionStore:
    sqla_engine: AsyncEngine = None
    neo4j_driver: AsyncDriver = None
    rbmq_channel_pool: Pool[Channel] = None


connection_store = ConnectionStore()
