from core.utils.settings import PostgresSettings, RabbitMQSettings


class Settings(RabbitMQSettings, PostgresSettings):
    HUGGING_FACE_TOKEN: str


settings = Settings()
