import gc
import json
import uuid
from datetime import datetime
from typing import List
from uuid import UUID

import torch
from diffusers import DDIMScheduler
from pika import spec
from pika.channel import Channel
from pydantic.json import pydantic_encoder

from core.constants import TASK_QUEUE_NAME, ExecTaskStatuses
from core.schemas.execution import Artifact, ExecutionStatus, ExecutionTask
from stable_diffusion.connection import connection_store
from stable_diffusion.interface import StableDiffusionInterface
from stable_diffusion.settings import settings

FILE_EXTENSION = ".jpg"

scheduler = DDIMScheduler(
    beta_start=0.00085,
    beta_end=0.012,
    beta_schedule="scaled_linear",
    clip_sample=False,
    set_alpha_to_one=False,
    steps_offset=1,
)

stable_diffusion_interface = StableDiffusionInterface(
    "CompVis/stable-diffusion-v1-4",
    scheduler=scheduler,
    use_auth_token=settings.HUGGING_FACE_TOKEN,
)


def apply_to_search(exec_task_id: UUID) -> None:
    session = connection_store.get_session()

    resp = session.post(f"{settings.API_URL}/search/apply/{exec_task_id}")

    if resp.status_code != 200:
        print("API error in apply_to_search: ", resp.text)


def set_status(exec_task_id: UUID, status: ExecTaskStatuses) -> None:
    session = connection_store.get_session()

    resp = session.post(
        f"{settings.API_URL}/exec/status/{exec_task_id}",
        data=ExecutionStatus(status=status, timestamp=datetime.utcnow()).json(),
    )

    if resp.status_code != 200:
        print("API error in set_status: ", resp.text)


def add_artifacts(exec_task_id: UUID, artifacts: List[Artifact]) -> None:
    session = connection_store.get_session()

    resp = session.post(
        f"{settings.API_URL}/exec/artifacts/{exec_task_id}",
        data=json.dumps(
            [artifact.dict() for artifact in artifacts], default=pydantic_encoder
        ),
    )
    if resp.status_code != 200:
        print("API error in add_artifacts: ", resp.text)


def on_message(
    channel: Channel,
    method_frame: spec.Basic.Deliver,
    _,
    body: bytes,
) -> None:
    exec_task = ExecutionTask.parse_raw(body)
    exec_payload = exec_task.payload

    set_status(exec_task.id_, ExecTaskStatuses.IN_PROGRESS)

    print("Task: ", exec_task.json())
    images = []
    try:
        images = stable_diffusion_interface(
            exec_payload.prompt,
            height=exec_payload.height,
            width=exec_payload.width,
            negative_prompt=exec_payload.negative_prompt,
            num_images_per_prompt=exec_payload.samples_num,
            num_inference_steps=exec_payload.steps_num,
            guidance_scale=exec_payload.guidance_scale,
            seed=exec_payload.seed,
        )

    except RuntimeError as e:
        if "CUDA" not in str(e):
            raise e

        print("CUDA error occurred!")
        print("Error: ", e)

        set_status(exec_task.id_, ExecTaskStatuses.ERROR)

        channel.basic_nack(delivery_tag=method_frame.delivery_tag)

    else:

        artifacts = []
        for image in images:
            img_id = uuid.uuid4()
            filename = f"{img_id}{FILE_EXTENSION}"

            image.save(f"/app/output/{filename}")

            artifacts.append(
                Artifact(
                    id_=img_id,
                    filename=filename,
                    timestamp=datetime.utcnow(),
                )
            )

        add_artifacts(exec_task.id_, artifacts)
        apply_to_search(exec_task.id_)

        set_status(exec_task.id_, ExecTaskStatuses.DONE)

        channel.basic_ack(delivery_tag=method_frame.delivery_tag)

    finally:
        torch.cuda.empty_cache()
        gc.collect()


def main():

    channel = connection_store.get_channel()

    channel.queue_declare(queue=TASK_QUEUE_NAME, durable=True)
    channel.basic_consume(TASK_QUEUE_NAME, on_message)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()


if __name__ == "__main__":
    main()
