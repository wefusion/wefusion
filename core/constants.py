from enum import Enum

# model defaults
DEFAULT_WIDTH = 512
DEFAULT_HEIGHT = 512
DEFAULT_STEPS_NUM = 35
DEFAULT_GUIDANCE_SCALE = 7.5
DEFAULT_SAMPLES_NUM = 1

# execution
TASK_QUEUE_NAME = "exec_tasks"


class ExecTaskStatuses(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    ERROR = "error"


class UserArtifactTypes(str, Enum):
    LIKED = "liked"
    GENERATED = "generated"
