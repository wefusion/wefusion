from typing import List

import neo4j
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.crud import artifact_crud, search_crud
from api.routes.providers import get_neo4j_session, get_sqla_session
from api.schemas.artifact import ArtifactOut
from core.utils.prompt_handler import split_prompt

router = APIRouter()


@router.get("/{input}", response_model=List[ArtifactOut])
async def search_by_input(
    input: str,
    *,
    neo4j_session: neo4j.AsyncSession = Depends(get_neo4j_session),
    sqla_session: AsyncSession = Depends(get_sqla_session)
):
    words = list(split_prompt(input))
    ids = await search_crud.search_by_input(neo4j_session, words=words)
    artifacts = await artifact_crud.get_by_ids(sqla_session, ids=ids)

    return artifacts
