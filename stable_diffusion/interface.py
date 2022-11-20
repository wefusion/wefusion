import torch
from diffusers import StableDiffusionPipeline


class StableDiffusionInterface:
    def __init__(
        self,
        model_name,
        scheduler,
        use_auth_token,
        revision="fp16",
        torch_dtype=torch.float32,
        safe_mode=False,
        device="cuda",
    ):
        self.pipe = StableDiffusionPipeline.from_pretrained(
            model_name,
            scheduler=scheduler,
            revision=revision,
            torch_dtype=torch_dtype,
            use_auth_token=use_auth_token,
        )

        if not safe_mode:
            self.pipe.safety_checker = lambda images, clip_input: (images, False)
        self.pipe.to(device)

    def __call__(
        self,
        prompt="",
        height=64,
        width=64,
        negative_prompt="",
        num_images_per_prompt=1,
        num_inference_steps=50,
        guidance_scale=7.5,
    ):
        return self.pipe(
            prompt,
            height=height,
            width=width,
            negative_prompt=negative_prompt,
            num_images_per_prompt=num_images_per_prompt,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
        ).images
