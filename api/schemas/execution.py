from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from core.constants import (
    DEFAULT_GUIDANCE_SCALE,
    DEFAULT_HEIGHT,
    DEFAULT_SAMPLES_NUM,
    DEFAULT_STEPS_NUM,
    DEFAULT_WIDTH,
    ExecTaskStatuses,
)
from core.schemas.execution import ExecutionPayload


class ExecutionIn(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = ""

    width: int = DEFAULT_WIDTH
    height: int = DEFAULT_HEIGHT
    steps_num: int = DEFAULT_STEPS_NUM
    samples_num: int = DEFAULT_SAMPLES_NUM
    guidance_scale: float = DEFAULT_GUIDANCE_SCALE
    seed: Optional[int] = None


class ExecutionOut(BaseModel):
    id_: UUID
    timestamp: datetime
    payload: ExecutionPayload
    status: ExecTaskStatuses


class ExecutionStatusOut(BaseModel):
    id_: UUID
    exec_timestamp: datetime
    last_update_timestamp: datetime
    payload: ExecutionPayload
    status: ExecTaskStatuses
