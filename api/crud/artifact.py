from typing import List

from sqlalchemy import join, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import Artifact, ExecTask, User


class ArtifactCRUD:
    async def get_by_user(
        self, session: AsyncSession, *, user: User, limit: int, skip: int
    ) -> List:
        sel_stmt = (
            select(Artifact.filename, ExecTask.payload, Artifact.timestamp)
            .select_from(
                join(Artifact, ExecTask, Artifact.exec_task_id == ExecTask.id_)
            )
            .where(Artifact.user_id == user.id_)
            .limit(limit)
            .offset(skip)
        )

        result = await session.execute(sel_stmt)

        return result.fetchall()
