from typing import List, Optional

from pydantic import BaseModel

from .artifact import ArtifactOut


class SearchBase(BaseModel):
    skip: int = 0
    limit: int = 30


class SearchPromptIn(SearchBase):
    prompt: str


class SearchInfinityIn(SearchBase):
    seed: Optional[float] = None


class SearchPromptOut(BaseModel):
    cursor: Optional[int]
    artifacts: List[ArtifactOut]


class SearchInfinityOut(BaseModel):
    cursor: Optional[int]
    seed: float
    artifacts: List[ArtifactOut]
