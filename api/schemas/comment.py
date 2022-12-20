from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ArtifactComment(BaseModel):
    comment: str


class ArtifactCommentIn(ArtifactComment):
    pass


class ArtifactCommentOut(ArtifactComment):
    user_id: UUID
    timestamp: datetime

    class Config:
        orm_mode = True
