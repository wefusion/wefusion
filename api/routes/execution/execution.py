import os
import re
from typing import List
from uuid import UUID

import aio_pika
from aio_pika.channel import Channel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.crud import exec_task_crud
from api.routes.providers import get_channel, get_current_user, get_sqla_session
from api.schemas.execution import ExecutionIn, ExecutionOut, ExecutionStatusOut
from core.constants import TASK_QUEUE_NAME
from core.models import User
from core.schemas.execution import ExecutionPayload, ExecutionTask

router = APIRouter()


def check_prompt(prompt: str) -> None:
    if not re.match(r"^[a-zA-Z0-9.,;\|&\s!-?]+$", prompt):
        raise HTTPException(
            status_code=400,
            detail="Prompt should contain only latin letters, numbers and punctuation marks: .,;|&-!?",
        )


@router.post("/", response_model=ExecutionOut)
async def create_execution(
    execution_in: ExecutionIn,
    *,
    channel: Channel = Depends(get_channel),
    session: AsyncSession = Depends(get_sqla_session),
    user: User = Depends(get_current_user),
):

    check_prompt(execution_in.prompt)
    if execution_in.negative_prompt:
        check_prompt(execution_in.negative_prompt)

    seed = execution_in.seed
    if seed is None:
        seed = int.from_bytes(os.urandom(6))

    exec_payload = ExecutionPayload(
        prompt=execution_in.prompt,
        negative_prompt=execution_in.negative_prompt,
        width=execution_in.width,
        height=execution_in.height,
        steps_num=execution_in.steps_num,
        guidance_scale=execution_in.guidance_scale,
        samples_num=execution_in.samples_num,
        seed=seed,
    )

    exec_task_obj, exec_task_status_obj = await exec_task_crud.create(
        session,
        payload_in=exec_payload,
        user=user,
    )

    exec_task = ExecutionTask(
        id_=exec_task_obj.id_,
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
        id_=exec_task_obj.id_,
        timestamp=exec_task_obj.timestamp,
        payload=exec_payload,
        status=exec_task_status_obj.status,
    )


@router.get("/status", response_model=List[ExecutionStatusOut])
async def get_last_statuses(
    limit: int = 100,
    skip: int = 0,
    *,
    session: AsyncSession = Depends(get_sqla_session),
    user: User = Depends(get_current_user),
):
    statuses = await exec_task_crud.get_last_statuses(
        session,
        user=user,
        limit=limit,
        skip=skip,
    )

    return statuses


@router.get("/status/{id_}", response_model=ExecutionStatusOut)
async def get_task_status(
    id_: UUID,
    *,
    session: AsyncSession = Depends(get_sqla_session),
):
    status = await exec_task_crud.get_status_by_id(session, id_=id_)

    return status
