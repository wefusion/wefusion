import re

import aio_pika
from aio_pika.channel import Channel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.crud import exec_task_crud
from api.routes.providers import get_channel, get_current_user, get_session
from api.schemas.execution import ExecutionIn, ExecutionOut
from core.constants import (
    DEFAULT_GUIDANCE_SCALE,
    DEFAULT_SAMPLES_NUM,
    DEFAULT_STEPS_NUM,
    MODEL_SEED,
    TASK_QUEUE_NAME,
)
from core.models import User
from core.schemas.execution import ExecutionTask

router = APIRouter()


def check_prompt(prompt: str) -> None:
    if not re.match(r"^[a-zA-Z0-9.,;\|&\s]+$", prompt):
        raise HTTPException(
            status_code=400,
            detail="Prompt should contain only latin letters, numbers and punctuation marks: .,;|&",
        )


@router.post("/", response_model=ExecutionOut)
async def create_execution(
    execution_in: ExecutionIn,
    *,
    channel: Channel = Depends(get_channel),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):

    check_prompt(execution_in.prompt)
    if execution_in.negative_prompt:
        check_prompt(execution_in.negative_prompt)

    exec_payload = ExecutionTask(
        prompt=execution_in.prompt,
        negative_prompt=execution_in.negative_prompt,
        width=execution_in.width,
        height=execution_in.height,
        steps_num=DEFAULT_STEPS_NUM,
        guidance_scale=DEFAULT_GUIDANCE_SCALE,
        samples_num=DEFAULT_SAMPLES_NUM,
        seed=MODEL_SEED,
    )

    exec_task_obj, exec_task_status_obj = await exec_task_crud.create(
        session,
        payload_in=exec_payload,
        user=user,
    )

    exec_task = ExecutionTask(
        id_=exec_task_obj.id,
        timestamp=exec_task_obj.timestamp,
        user_id=exec_task_obj.user_id,
        payload=exec_task_obj.payload,
    )

    await channel.declare_queue(TASK_QUEUE_NAME, durable=True)
    await channel.default_exchange.publish(
        aio_pika.Message(
            body=exec_task.json().encode(),
            content_type="application/json",
        ),
        routing_key=TASK_QUEUE_NAME,
    )

    return ExecutionOut(
        id=exec_task_obj.id,
        timestamp=exec_task_obj.timestamp,
        payload=exec_payload,
        status=exec_task_status_obj.status,
    )
