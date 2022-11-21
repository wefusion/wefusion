from .exec_task import ExecTaskCRUD
from .user import UserCRUD

user_crud = UserCRUD()
exec_task_crud = ExecTaskCRUD()

__all__ = ["user_crud"]
