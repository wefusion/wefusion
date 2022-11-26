import gc
import uuid
from uuid import UUID

import pika
import torch
from diffusers import DDIMScheduler
from pika import BlockingConnection, spec
from pika.channel import Channel
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from core.constants import TASK_QUEUE_NAME, ExecTaskStatuses
from core.models import Artifact, ExecTaskStatus
from core.schemas.execution import ExecutionTask
from stable_diffusion.interface import StableDiffusionInterface
from stable_diffusion.settings import settings

FILE_EXTENSION = ".jpg"

scheduler = DDIMScheduler(
    beta_start=0.00085,
    beta_end=0.012,
    beta_schedule="scaled_linear",
    clip_sample=False,
    set_alpha_to_one=False,
)

stable_diffusion_interface = StableDiffusionInterface(
    "CompVis/stable-diffusion-v1-4",
    scheduler=scheduler,
    use_auth_token=settings.HUGGING_FACE_TOKEN,
)


class ConnectionStore:
    _rabbitmq_conn: BlockingConnection
    _sqla_engine: Engine

    def __init__(self):
        pika_conn_params = pika.URLParameters(settings.RABBITMQ_DSN)
        self._rabbitmq_conn = pika.BlockingConnection(pika_conn_params)
        self._sqla_engine = create_engine(settings.POSTGRES_DSN)

    def get_channel(self):
        return self._rabbitmq_conn.channel()

    def get_session(self) -> Session:
        return Session(bind=self._sqla_engine)


connection_store = ConnectionStore()


def set_status(exec_task_id: UUID, status: ExecTaskStatuses):
    with connection_store.get_session() as session:
        status_obj = ExecTaskStatus(
            exec_task_id=exec_task_id,
            status=status,
        )

        session.add(status_obj)
        session.commit()


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

    for image in images:
        img_id = uuid.uuid4()
        filename = f"{img_id}{FILE_EXTENSION}"
        image.save(f"/app/output/{filename}")

        with connection_store.get_session() as session:
            artifact_obj = Artifact(
                id_=img_id,
                filename=filename,
                exec_task_id=exec_task.id_,
                user_id=exec_task.user_id,
            )

            session.add(artifact_obj)
            session.commit()

    set_status(exec_task.id_, ExecTaskStatuses.DONE)

    torch.cuda.empty_cache()
    gc.collect()

    channel.basic_ack(delivery_tag=method_frame.delivery_tag)


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
