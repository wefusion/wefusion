from core.utils.settings import Neo4jSettings, PostgresSettings, RabbitMQSettings


class Settings(RabbitMQSettings, PostgresSettings, Neo4jSettings):
    HUGGING_FACE_TOKEN: str


settings = Settings()
