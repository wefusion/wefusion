from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.crud import artifact_crud
from api.routes.providers import get_current_user, get_sqla_session
from api.schemas.artifact import ArtifactOut
from core.models import User

router = APIRouter()


@router.get("/", response_model=List[ArtifactOut])
async def get_gallery(
    limit: int = 100,
    offset: int = 0,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_sqla_session),
):
    artifacts_obj = await artifact_crud.get_by_user(
        session, user=user, limit=limit, skip=offset
    )

    return artifacts_obj


@router.get("/{artifact_id}", response_model=ArtifactOut)
async def get_artifact(
    artifact_id: UUID,
    *,
    session: AsyncSession = Depends(get_sqla_session),
):
    artifact_obj = await artifact_crud.get_by_id(session, id_=artifact_id)

    return artifact_obj
