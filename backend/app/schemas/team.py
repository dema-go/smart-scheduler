from pydantic import BaseModel, ConfigDict
from typing import List, Optional


class TeamBase(BaseModel):
    name: str
    description: Optional[str] = None


class TeamCreate(TeamBase):
    pass


class TeamUpdate(TeamBase):
    is_active: Optional[bool] = None


class TeamResponse(TeamBase):
    id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class TeamWithEmployeeCount(TeamResponse):
    employee_count: int = 0
