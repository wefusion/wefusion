import re

import aio_pika
from aio_pika.channel import Channel
from fastapi import APIRouter, Depends, HTTPException

from api.routes.providers import get_channel
from api.schemas.execution import ExecutionIn, ExecutionOut
from core.constants import (
    DEFAULT_GUIDANCE_SCALE,
    DEFAULT_SAMPLES_NUM,
    DEFAULT_STEPS_NUM,
    MODEL_SEED,
    TASK_QUEUE_NAME,
)

router = APIRouter()


def check_prompt(prompt: str) -> None:
    if not re.match(r"^[a-zA-Z0-9.,;\|&\s]+$", prompt):
        raise HTTPException(
            status_code=400,
            detail="Prompt should contain only latin letters, numbers and punctuation marks: .,;|&",
        )


@router.post("/", response_model=ExecutionOut)
async def create_execution(
    execution_in: ExecutionIn, *, channel: Channel = Depends(get_channel)
):

    check_prompt(execution_in.prompt)
    if execution_in.negative_prompt:
        check_prompt(execution_in.negative_prompt)

    exec_task = ExecutionOut(
        prompt=execution_in.prompt,
        negative_prompt=execution_in.negative_prompt,
        width=execution_in.width,
        height=execution_in.height,
        steps_num=DEFAULT_STEPS_NUM,
        guidance_scale=DEFAULT_GUIDANCE_SCALE,
        samples_num=DEFAULT_SAMPLES_NUM,
        seed=MODEL_SEED,
    )

    await channel.declare_queue(TASK_QUEUE_NAME, durable=True)
    await channel.default_exchange.publish(
        aio_pika.Message(
            body=exec_task.json().encode(), content_type="application/json"
        ),
        routing_key=TASK_QUEUE_NAME,
    )

    return exec_task
