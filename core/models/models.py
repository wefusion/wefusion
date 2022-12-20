from datetime import datetime
from typing import Any, Callable, List, Optional, Tuple, Type, TypeVar, Union
from uuid import uuid4

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    MetaData,
    PrimaryKeyConstraint,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, as_declarative, declared_attr

from core.models.types import PydanticType
from core.schemas.execution import ExecutionPayload

convention = {
    "ix": "ix__%(column_0_N_name)s",
    "uq": "uq__%(table_name)s__%(column_0_N_name)s",
    "ck": "ck__%(table_name)s__%(constraint_name)s",
    "fk": "fk__%(table_name)s__%(referred_table_name)s__%(column_0_name)s",
    "pk": "pk__%(table_name)s__%(column_0_N_name)s",
}

metadata = MetaData(naming_convention=convention)
SCHEMA = "wefusion"

_T_Model = TypeVar("_T_Model")

_T_ColumnCollectionConstraint = Union[
    Index, PrimaryKeyConstraint, UniqueConstraint, CheckConstraint
]
_T_TableExtra = Union[
    _T_ColumnCollectionConstraint,
    Callable[[Type[_T_Model]], _T_ColumnCollectionConstraint],
]


@as_declarative(metadata=metadata)
class Base:
    __extra__: Tuple[Any, ...]
    __schema__: str = SCHEMA

    def __init_subclass__(
        cls, *args, extra: Optional[List[_T_TableExtra]] = None, **kwargs
    ) -> None:
        if extra is None:
            extra = []

        cls.__extra__ = tuple(obj(cls) if callable(obj) else obj for obj in extra)

    @declared_attr
    def __table_args__(cls):
        return (
            *cls.__extra__,
            {"schema": cls.__schema__},
        )


class User(Base):
    __tablename__ = "user"

    id_ = Column("id", UUID(as_uuid=True), primary_key=True, default=uuid4)
    first_name = Column(String(50), nullable=False)
    second_name = Column(String(50))
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    password_hash = Column(String(64), nullable=False)
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.now,
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
    )


class ExecTask(Base):
    __tablename__ = "exec_task"

    id_ = Column(
        "id",
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(f"{SCHEMA}.user.id"),
        nullable=False,
    )
    timestamp = Column(
        DateTime,
        nullable=False,
        default=datetime.now,
    )
    payload: Mapped[ExecutionPayload] = Column(
        PydanticType(ExecutionPayload), nullable=False
    )


class ExecTaskStatus(Base):
    __tablename__ = "exec_task_status"

    id_ = Column(
        "id",
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    exec_task_id = Column(
        UUID(as_uuid=True),
        ForeignKey(f"{SCHEMA}.exec_task.id"),
        nullable=False,
    )
    status = Column(
        String(50),
        nullable=False,
    )
    timestamp = Column(
        DateTime,
        nullable=False,
        default=datetime.now,
    )


class Artifact(Base):
    __tablename__ = "artifact"

    id_ = Column(
        "id",
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    filename = Column(
        String(70),
        nullable=False,
    )
    exec_task_id = Column(
        UUID(as_uuid=True),
        ForeignKey(f"{SCHEMA}.exec_task.id"),
        nullable=False,
    )
    timestamp = Column(
        DateTime,
        nullable=False,
        default=datetime.now,
    )


class UserArtifact(
    Base,
    extra=[
        PrimaryKeyConstraint("user_id", "artifact_id"),
        Index("ix__user_id_type", "user_id", "type"),
        Index("ix__user_id_artifact_id_type", "user_id", "artifact_id", "type"),
    ],
):
    __tablename__ = "user_artifact"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(f"{SCHEMA}.user.id"),
        nullable=False,
    )
    artifact_id = Column(
        UUID(as_uuid=True),
        ForeignKey(f"{SCHEMA}.artifact.id"),
        nullable=False,
    )
    type_ = Column("type", String(50), nullable=False)
    timestamp = Column(
        DateTime,
        nullable=False,
        default=datetime.now,
    )


class UserArtifactComment(Base):
    __tablename__ = "user_artifact_comment"

    id_ = Column(
        "id",
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(f"{SCHEMA}.user.id"),
        nullable=False,
    )
    artifact_id = Column(
        UUID(as_uuid=True),
        ForeignKey(f"{SCHEMA}.artifact.id"),
        nullable=False,
        index=True,
    )
    comment = Column(
        String(1024),
        nullable=False,
    )
    timestamp = Column(
        DateTime,
        nullable=False,
        default=datetime.now,
    )
