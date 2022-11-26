from .artifact import ArtifactCRUD
from .execution import ExecTaskCRUD
from .user import UserCRUD

user_crud = UserCRUD()
exec_task_crud = ExecTaskCRUD()
artifact_crud = ArtifactCRUD()

__all__ = ["user_crud", "exec_task_crud", "artifact_crud"]
