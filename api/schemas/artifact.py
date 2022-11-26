from datetime import datetime

from pydantic import BaseModel

from core.schemas.execution import ExecutionPayload


class ArtifactOut(BaseModel):
    filename: str
    payload: ExecutionPayload
    timestamp: datetime

    class Config:
        orm_mode = True
