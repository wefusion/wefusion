from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import join, select
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession

from core.constants import ExecTaskStatuses
from core.models.models import ExecTask, ExecTaskStatus, User
from core.schemas.execution import ExecutionPayload, ExecutionStatus


class ExecTaskCRUD:
    async def get_by_id(
        self, session: AsyncSession, *, id_: UUID
    ) -> Optional[ExecTask]:
        sel_stmt = select(ExecTask).where(ExecTask.id_ == id_)

        result = await session.execute(sel_stmt)

        return result.scalars().first()

    async def get_last_statuses(
        self, session: AsyncSession, *, user: User, limit: int, skip: int
    ) -> List[Row]:
        sub_sel_stmt = (
            select(
                ExecTask.id_,
                ExecTask.timestamp.label("exec_timestamp"),
                ExecTask.payload,
                ExecTaskStatus.timestamp.label("last_update_timestamp"),
                ExecTaskStatus.status,
            )
            .distinct(ExecTask.id_)
            .select_from(
                join(
                    ExecTaskStatus,
                    ExecTask,
                    ExecTaskStatus.exec_task_id == ExecTask.id_,
                )
            )
            .where(ExecTask.user_id == user.id_)
            .order_by(ExecTask.id_, ExecTaskStatus.timestamp.desc())
            .subquery()
        )

        sel_stmt = (
            select(sub_sel_stmt)
            .order_by(sub_sel_stmt.c.last_update_timestamp.desc())
            .limit(limit)
            .offset(skip)
        )

        result = await session.execute(sel_stmt)

        return result.fetchall()

    async def get_status_by_id(self, session: AsyncSession, *, id_: UUID) -> Row:
        sub_sel_stmt = (
            select(
                ExecTask.id_,
                ExecTask.timestamp.label("exec_timestamp"),
                ExecTask.payload,
                ExecTaskStatus.timestamp.label("last_update_timestamp"),
                ExecTaskStatus.status,
            )
            .distinct(ExecTask.id_)
            .select_from(
                join(
                    ExecTaskStatus,
                    ExecTask,
                    ExecTaskStatus.exec_task_id == ExecTask.id_,
                )
            )
            .where(ExecTask.id_ == id_)
            .order_by(ExecTask.id_, ExecTaskStatus.timestamp.desc())
        )

        result = await session.execute(sub_sel_stmt)

        return result.fetchone()

    async def set_status_by_id(
        self,
        session: AsyncSession,
        *,
        id_: UUID,
        status: ExecutionStatus,
    ) -> None:
        exec_task_status_obj = ExecTaskStatus(
            exec_task_id=id_,
            status=status.status.value,
            timestamp=status.timestamp,
        )

        session.add(exec_task_status_obj)

        await session.commit()

    async def create(
        self,
        session: AsyncSession,
        *,
        payload_in: ExecutionPayload,
        user: User,
    ) -> Tuple[ExecTask, ExecTaskStatus]:
        exec_task_obj = ExecTask(
            user_id=user.id_,
            payload=payload_in,
        )
        session.add(exec_task_obj)

        await session.commit()
        await session.refresh(exec_task_obj)

        exec_task_status_obj = ExecTaskStatus(
            exec_task_id=exec_task_obj.id_,
            status=ExecTaskStatuses.PENDING.value,
        )

        session.add(exec_task_status_obj)

        await session.commit()
        await session.refresh(exec_task_status_obj)

        return exec_task_obj, exec_task_status_obj
