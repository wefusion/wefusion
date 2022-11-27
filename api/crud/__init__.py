from .artifact import ArtifactCRUD
from .execution import ExecTaskCRUD
from .search import SearchCRUD
from .user import UserCRUD

user_crud = UserCRUD()
exec_task_crud = ExecTaskCRUD()
artifact_crud = ArtifactCRUD()
search_crud = SearchCRUD()

__all__ = ["user_crud", "exec_task_crud", "artifact_crud", "search_crud"]
