from typing import Optional

from pydantic import BaseModel

from core.constants import DEFAULT_HEIGHT, DEFAULT_WIDTH
from core.schemas.execution import ExecutionTask


class ExecutionIn(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = ""

    width: int = DEFAULT_WIDTH
    height: int = DEFAULT_HEIGHT


class ExecutionOut(ExecutionTask):
    pass
