from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.models import UserArtifactComment


class CommentCRUD:
    async def get_by_artifact_id(
        self,
        session: AsyncSession,
        *,
        artifact_id: UUID,
        limit: int,
        skip: int,
    ) -> List[UserArtifactComment]:
        sel_stmt = (
            select(UserArtifactComment)
            .where(UserArtifactComment.artifact_id == artifact_id)
            .offset(skip)
            .limit(limit)
        )

        result = await session.execute(sel_stmt)

        return result.scalars().all()

    async def create(
        self,
        session: AsyncSession,
        *,
        artifact_id: UUID,
        user_id: UUID,
        comment: str,
    ) -> UserArtifactComment:
        comment_obj = UserArtifactComment(
            artifact_id=artifact_id, user_id=user_id, comment=comment
        )

        session.add(comment_obj)
        await session.commit()
        await session.refresh(comment_obj)

        return comment_obj
