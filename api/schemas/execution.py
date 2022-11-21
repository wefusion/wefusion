from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from core.constants import DEFAULT_HEIGHT, DEFAULT_WIDTH, ExecTaskStatuses
from core.schemas.execution import ExecutionPayload


class ExecutionIn(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = ""

    width: int = DEFAULT_WIDTH
    height: int = DEFAULT_HEIGHT


class ExecutionOut(BaseModel):
    id_: UUID = Field(..., alias="id")
    timestamp: datetime
    payload: ExecutionPayload
    status: ExecTaskStatuses
