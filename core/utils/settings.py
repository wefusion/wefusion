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
