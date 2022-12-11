from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, delete, join, select
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession

from core.constants import UserArtifactTypes
from core.models import Artifact, ExecTask, UserArtifact


class ArtifactCRUD:
    async def get_by_id(self, session: AsyncSession, *, id_: UUID) -> Optional[Row]:
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

    async def get_by_user_id(
        self,
        session: AsyncSession,
        *,
        user_id: UUID,
        type_: UserArtifactTypes,
        limit: int,
        skip: int,
    ) -> List[Row]:
        sel_stmt = (
            select(Artifact.filename, ExecTask.payload, Artifact.timestamp)
            .select_from(
                join(
                    UserArtifact,
                    Artifact,
                    UserArtifact.artifact_id == Artifact.id_,
                    isouter=True,
                ).join(ExecTask, Artifact.exec_task_id == ExecTask.id_, isouter=True)
            )
            .where(
                and_(
                    UserArtifact.user_id == user_id,
                    UserArtifact.type_ == type_.value,
                )
            )
            .limit(limit)
            .offset(skip)
        )

        result = await session.execute(sel_stmt)

        return result.fetchall()

    async def link_to_user_by_id(
        self,
        session: AsyncSession,
        *,
        user_id: UUID,
        artifact_id: UUID,
        type_: UserArtifactTypes,
    ) -> None:
        user_artifact = UserArtifact(
            user_id=user_id,
            artifact_id=artifact_id,
            type_=type_.value,
        )

        session.add(user_artifact)
        await session.commit()

    async def unlink_from_user_by_id(
        self,
        session: AsyncSession,
        *,
        user_id: UUID,
        artifact_id: UUID,
        type_: UserArtifactTypes,
    ) -> None:
        del_stmt = delete(UserArtifact).where(
            and_(
                UserArtifact.user_id == user_id,
                UserArtifact.artifact_id == artifact_id,
                UserArtifact.type_ == type_.value,
            )
        )

        await session.execute(del_stmt)
        await session.commit()

    async def get_link_to_user(
        self, session: AsyncSession, *, user_id: UUID, artifact_id: UUID
    ) -> UserArtifact:
        sel_stmt = select(UserArtifact).where(
            and_(
                UserArtifact.user_id == user_id,
                UserArtifact.artifact_id == artifact_id,
            )
        )

        result = await session.execute(sel_stmt)

        return result.scalar()
