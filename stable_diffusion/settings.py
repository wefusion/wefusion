from core.utils.settings import RabbitMQSettings


class Settings(RabbitMQSettings):
    HUGGING_FACE_TOKEN: str


settings = Settings()
