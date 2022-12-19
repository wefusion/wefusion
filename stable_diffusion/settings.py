from typing import Optional

from pydantic import Field, validator

from core.utils.settings import RabbitMQSettings


class Settings(RabbitMQSettings):
    HUGGING_FACE_TOKEN: str
    API_HOST: str
    API_PORT: str
    SERVICE_KEY: str = Field(..., env="API_SERVICE_KEY")

    API_URL: Optional[str] = None

    @validator("API_URL", pre=False)
    def assemble_api_url(cls, v: Optional[str], values: dict) -> str:
        if isinstance(v, str):
            return v

        return f"http://{values.get('API_HOST')}:{values.get('API_PORT')}/api"


settings = Settings()
