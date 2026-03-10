from pydantic import BaseModel, ConfigDict
from typing import Optional


class ShiftTypeBase(BaseModel):
    name: str
    start_time: str
    end_time: str
    color: str = "#409EFF"
    required_count: int = 1


class ShiftTypeCreate(ShiftTypeBase):
    pass


class ShiftTypeUpdate(ShiftTypeBase):
    is_active: Optional[bool] = None


class ShiftTypeResponse(ShiftTypeBase):
    id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
