from typing import List, Optional
from uuid import UUID

from sqlalchemy import join, select
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import Artifact, ExecTask, User


class ArtifactCRUD:
    async def get_by_user(
        self, session: AsyncSession, *, user: User, limit: int, skip: int
    ) -> List[Row]:
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

    async def get_by_id(self, session: AsyncSession, *, id_: int) -> Optional[Row]:
        sel_stmt = (
            select(Artifact.filename, ExecTask.payload, Artifact.timestamp)
            .select_from(
                join(Artifact, ExecTask, Artifact.exec_task_id == ExecTask.id_)
            )
            .where(Artifact.id_ == id_)
        )

        result = await session.execute(sel_stmt)

        return result.fetchone()

    async def get_by_ids(self, session: AsyncSession, *, ids: List[UUID]) -> List[Row]:
        sel_stmt = (
            select(Artifact.filename, ExecTask.payload, Artifact.timestamp)
            .select_from(
                join(Artifact, ExecTask, Artifact.exec_task_id == ExecTask.id_)
            )
            .where(Artifact.id_.in_(ids))
        )

        result = await session.execute(sel_stmt)

        return result.fetchall()
