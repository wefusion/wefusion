from typing import List
from uuid import UUID

import neo4j
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.crud import artifact_crud, exec_task_crud, search_crud
from api.routes.providers import api_key_auth, get_neo4j_session, get_sqla_session
from api.schemas.artifact import ArtifactOut
from core.utils.prompt_handler import split_prompt

router = APIRouter()


@router.get(
    "/{input_}",
    response_model=List[ArtifactOut],
)
async def search_by_input(
    input_: str,
    *,
    neo4j_session: neo4j.AsyncSession = Depends(get_neo4j_session),
    sqla_session: AsyncSession = Depends(get_sqla_session)
):
    words = list(split_prompt(input_))
    ids = await search_crud.search_by_input(neo4j_session, words=words)
    artifacts = await artifact_crud.get_by_ids(sqla_session, ids=ids)

    return artifacts


@router.post(
    "/apply/{exec_task_id}",
    status_code=200,
    dependencies=[Depends(api_key_auth)],
    tags=["Internal"],
)
async def apply_search(
    exec_task_id: UUID,
    *,
    neo4j_session: neo4j.AsyncSession = Depends(get_neo4j_session),
    sqla_session: AsyncSession = Depends(get_sqla_session)
):
    exec_obj = await exec_task_crud.get_by_id(sqla_session, id_=exec_task_id)
    if not exec_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execution task not found",
        )

    artifacts = await artifact_crud.get_by_execution_id(sqla_session, id_=exec_task_id)
    if not artifacts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artifacts not found",
        )

    words = list(split_prompt(exec_obj.payload.prompt))

    await search_crud.apply_search(
        neo4j_session, words=words, ids=[a.id_ for a in artifacts]
    )
