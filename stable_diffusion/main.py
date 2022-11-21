import datetime
import zoneinfo

import pika
from diffusers import DDIMScheduler
from pika import spec
from pika.channel import Channel

from core.constants import TASK_QUEUE_NAME
from core.schemas.execution import ExecutionTask
from stable_diffusion.interface import StableDiffusionInterface
from stable_diffusion.settings import settings


def main():
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

    connection_params = pika.URLParameters(settings.RABBITMQ_DSN)
    connection = pika.BlockingConnection(connection_params)

    channel = connection.channel()

    def on_message(
        channel: Channel, method_frame: spec.Basic.Deliver, _, body: bytes
    ) -> None:
        exec_task = ExecutionTask.parse_raw(body)

        images = stable_diffusion_interface(
            exec_task.prompt,
            height=exec_task.height,
            width=exec_task.width,
            negative_prompt=exec_task.negative_prompt,
            num_images_per_prompt=exec_task.samples_num,
            num_inference_steps=exec_task.steps_num,
            guidance_scale=exec_task.guidance_scale,
            seed=exec_task.seed,
        )

        for image in images:
            filename = (
                datetime.datetime.now(zoneinfo.ZoneInfo("Europe/Moscow"))
                .strftime("%Y-%m-%d %H:%M:%S.%f")
                .replace(":", "-")
            )
            image.save(f"/app/output/{filename}.jpg")

        channel.basic_ack(delivery_tag=method_frame.delivery_tag)

    channel.queue_declare(queue=TASK_QUEUE_NAME, durable=True)
    channel.basic_consume(TASK_QUEUE_NAME, on_message)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    connection.close()


if __name__ == "__main__":
    main()
