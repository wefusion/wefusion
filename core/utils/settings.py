from typing import Any, Dict, Optional

from pydantic import AmqpDsn, BaseSettings, PostgresDsn, validator


class PostgresSettings(BaseSettings):
    POSTGRES_DRIVER: str = "psycopg2"

    POSTGRES_HOST: str
    POSTGRES_PORT: str

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    POSTGRES_DB: str

    POSTGRES_DSN: Optional[str] = None

    @validator("POSTGRES_DSN", pre=False)
    def assemble_postgres_dsn(
        cls,
        v: Optional[str],
        values: Dict[str, Any],
    ) -> str:
        if isinstance(v, str):
            return v

        return PostgresDsn.build(
            scheme=f"postgresql+{values.get('POSTGRES_DRIVER')}",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_HOST"),
            port=values.get("POSTGRES_PORT"),
            path=f"/{values.get('POSTGRES_DB')}",
        )

    class Config:
        env_file = ".env"


class RabbitMQSettings(BaseSettings):
    RABBITMQ_HOST: str
    RABBITMQ_PORT: str

    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: str

    RABBITMQ_DSN: Optional[str] = None

    @validator("RABBITMQ_DSN", pre=False)
    def assemble_rabbitmq_dsn(
        cls,
        v: Optional[str],
        values: Dict[str, Any],
    ) -> str:
        if isinstance(v, str):
            return v

        return AmqpDsn.build(
            scheme="amqp",
            user=values.get("RABBITMQ_USER"),
            password=values.get("RABBITMQ_PASSWORD"),
            host=values.get("RABBITMQ_HOST"),
            port=values.get("RABBITMQ_PORT"),
        )

    class Config:
        env_file = ".env"


class Neo4jSettings(BaseSettings):
    NEO4J_HOST: str
    NEO4J_PORT: str
    NEO4J_USER: str
    NEO4J_PASSWORD: str

    NEO4J_URI: Optional[str] = None

    @validator("NEO4J_URI", pre=False)
    def assemble_neo4j_uri(
        cls,
        v: Optional[str],
        values: Dict[str, Any],
    ) -> str:
        if isinstance(v, str):
            return v

        return f"bolt://{values.get('NEO4J_HOST')}:{values.get('NEO4J_PORT')}"

    class Config:
        env_file = ".env"
