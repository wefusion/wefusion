from typing import Dict, Generic, Optional, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy import types

_MT = TypeVar("_MT", bound=BaseModel)


class PydanticType(types.TypeDecorator, Generic[_MT]):
    impl = types.JSON
    cache_ok = True

    pydantic_type: Type[_MT]

    def __init__(self, pydantic_type: Type[_MT]):
        super().__init__()
        self.pydantic_type = pydantic_type

    def process_bind_param(self, value: Optional[_MT], _) -> Optional[Dict]:
        return value.dict() if value else None

    def process_result_value(self, value: Optional[Dict], _) -> Optional[_MT]:
        return self.pydantic_type.parse_obj(value) if value else None
