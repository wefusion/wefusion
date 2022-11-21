from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ExecutionPayload(BaseModel):
    prompt: str
    negative_prompt: str
    width: int
    height: int
    steps_num: int
    samples_num: int
    guidance_scale: float
    seed: Optional[int]


class ExecutionTask(BaseModel):
    id_: UUID
    user_id: UUID
    payload: ExecutionPayload
    timestamp: datetime
