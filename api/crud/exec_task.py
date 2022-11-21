from typing import Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from core.constants import ExecTaskStatuses
from core.models import ExecTask, ExecTaskStatus, User
from core.schemas.execution import ExecutionPayload


class ExecTaskCRUD:
    async def create(
        self, db: AsyncSession, *, payload_in: ExecutionPayload, user: User
    ) -> Tuple[ExecTask, ExecTaskStatus]:
        exec_task_obj = ExecTask(
            user_id=user.id,
            payload=payload_in.dict(),
        )
        db.add(exec_task_obj)

        await db.commit()
        await db.refresh(exec_task_obj)

        exec_task_status_obj = ExecTaskStatus(
            exec_task_id=exec_task_obj.id,
            status=ExecTaskStatuses.PENDING.value,
        )

        db.add(exec_task_status_obj)

        await db.commit()
        await db.refresh(exec_task_status_obj)

        return exec_task_obj, exec_task_status_obj
