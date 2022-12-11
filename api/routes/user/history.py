from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.crud import artifact_crud
from api.routes.providers import get_current_user, get_sqla_session
from api.schemas.artifact import ArtifactOut
from core.constants import UserArtifactTypes
from core.models import User

router = APIRouter()


@router.get("/", response_model=List[ArtifactOut])
async def get_history(
    limit: int = 100,
    offset: int = 0,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_sqla_session),
):
    artifacts_obj = await artifact_crud.get_by_user_id(
        session,
        user_id=user.id_,
        type_=UserArtifactTypes.GENERATED,
        limit=limit,
        skip=offset,
    )

    return artifacts_obj


@router.delete("/{artifact_id}", status_code=204)
async def remove_from_history(
    artifact_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_sqla_session),
):
    artifact_obj = await artifact_crud.get_by_id(session, artifact_id=artifact_id)
    if not artifact_obj:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artifact not found",
        )

    await artifact_crud.unlink_from_user_by_id(
        session,
        user_id=user.id_,
        artifact_id=artifact_id,
        type_=UserArtifactTypes.GENERATED,
    )
