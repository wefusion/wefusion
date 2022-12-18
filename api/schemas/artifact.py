from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from core.schemas.execution import ExecutionPayload


class ArtifactOut(BaseModel):
    id_: UUID
    filename: str
    payload: ExecutionPayload
    timestamp: datetime

    class Config:
        orm_mode = True
