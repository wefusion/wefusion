import gc
import uuid
from typing import List
from uuid import UUID

import torch
from diffusers import DDIMScheduler
from neo4j import ManagedTransaction
from pika import spec
from pika.channel import Channel

from core.constants import TASK_QUEUE_NAME, ExecTaskStatuses
from core.models import Artifact, ExecTaskStatus
from core.schemas.execution import ExecutionTask
from core.utils.prompt_handler import split_prompt
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
)

stable_diffusion_interface = StableDiffusionInterface(
    "CompVis/stable-diffusion-v1-4",
    scheduler=scheduler,
    use_auth_token=settings.HUGGING_FACE_TOKEN,
)


def add_to_search(artifact_id: UUID, words: List[str]) -> None:
    def _add_to_search(tx: ManagedTransaction, artifact_id: UUID, words: List[str]):
        q = 'CREATE (a:Artifact {id: "%s"})\n' % artifact_id
        for i, word in enumerate(words):
            q += 'MERGE (t%i:Tag {name: "%s"}) CREATE (a)-[:HAVE]->(t%i)\n' % (
                i,
                word,
                i,
            )

        tx.run(q)

    session = connection_store.get_neo4j_session()
    session.execute_write(_add_to_search, artifact_id, words)


def set_status(exec_task_id: UUID, status: ExecTaskStatuses) -> None:
    session = connection_store.get_sqla_session()
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

    session = connection_store.get_sqla_session()
    for image in images:
        img_id = uuid.uuid4()
        filename = f"{img_id}{FILE_EXTENSION}"
        image.save(f"/app/output/{filename}")

        artifact_obj = Artifact(
            id_=img_id,
            filename=filename,
            exec_task_id=exec_task.id_,
            user_id=exec_task.user_id,
        )

        session.add(artifact_obj)

        words = split_prompt(exec_payload.prompt)
        add_to_search(img_id, words)

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
