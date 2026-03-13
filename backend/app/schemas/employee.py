from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import date


class EmployeeBase(BaseModel):
    name: str
    position: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    available_days: List[int] = []
    preferred_shifts: List[int] = []
    available_start_time: Optional[str] = None
    available_end_time: Optional[str] = None
    preference_note: Optional[str] = None
    team_id: Optional[int] = None


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(EmployeeBase):
    is_active: Optional[bool] = None


class EmployeeResponse(EmployeeBase):
    id: int
    is_active: bool
    team_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class EmployeeWithScheduleCount(EmployeeResponse):
    schedule_count: int = 0
