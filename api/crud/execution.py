from typing import List, Tuple
from uuid import UUID

from sqlalchemy import join, select
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession

from core.constants import ExecTaskStatuses
from core.models import ExecTask, ExecTaskStatus, User
from core.schemas.execution import ExecutionPayload


class ExecTaskCRUD:
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

    async def create(
        self, db: AsyncSession, *, payload_in: ExecutionPayload, user: User
    ) -> Tuple[ExecTask, ExecTaskStatus]:
        exec_task_obj = ExecTask(
            user_id=user.id_,
            payload=payload_in.dict(),
        )
        db.add(exec_task_obj)

        await db.commit()
        await db.refresh(exec_task_obj)

        exec_task_status_obj = ExecTaskStatus(
            exec_task_id=exec_task_obj.id_,
            status=ExecTaskStatuses.PENDING.value,
        )

        db.add(exec_task_status_obj)

        await db.commit()
        await db.refresh(exec_task_status_obj)

        return exec_task_obj, exec_task_status_obj
