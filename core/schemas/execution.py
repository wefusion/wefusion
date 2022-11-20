from pydantic import BaseModel


class ExecutionTask(BaseModel):
    prompt: str
    negative_prompt: str
    width: int
    height: int
    steps_num: int
    samples_num: int
    guidance_scale: float
    seed: int
