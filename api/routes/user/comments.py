from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.crud import artifact_crud, comment_crud
from api.routes.providers import get_current_user, get_sqla_session, user_token_auth
from api.schemas.comment import ArtifactCommentIn, ArtifactCommentOut
from core.models.models import User

router = APIRouter()


@router.get(
    "/{artifact_id}",
    response_model=List[ArtifactCommentOut],
    dependencies=[Depends(user_token_auth)],
)
async def get_artifact_comments(
    artifact_id: UUID,
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_sqla_session),
):
    artifact_obj = await artifact_crud.get_by_id(session, id_=artifact_id)
    if not artifact_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artifact not found",
        )

    comments = await comment_crud.get_by_artifact_id(
        session, artifact_id=artifact_id, limit=limit, skip=offset
    )

    return comments


@router.post(
    "/{artifact_id}",
    response_model=ArtifactCommentOut,
)
async def create_artifact_comment(
    artifact_id: UUID,
    comment_in: ArtifactCommentIn,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_sqla_session),
):
    artifact_obj = await artifact_crud.get_by_id(session, id_=artifact_id)
    if not artifact_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artifact not found",
        )

    comment = await comment_crud.create(
        session,
        artifact_id=artifact_id,
        user_id=user.id_,
        comment=comment_in.comment,
    )

    return comment
