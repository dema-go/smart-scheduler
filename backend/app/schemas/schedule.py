from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date


class ScheduleBase(BaseModel):
    employee_id: int
    shift_type_id: int
    date: date


class ScheduleCreate(ScheduleBase):
    pass


class ScheduleUpdate(BaseModel):
    employee_id: Optional[int] = None
    shift_type_id: Optional[int] = None
    date: Optional[date] = None


class ScheduleResponse(ScheduleBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ScheduleWithDetails(ScheduleResponse):
    employee_name: str = ""
    shift_name: str = ""
    shift_color: str = ""
