from fastapi import APIRouter
from app.api import employee, shift, schedule, team

api_router = APIRouter()
api_router.include_router(employee.router)
api_router.include_router(shift.router)
api_router.include_router(schedule.router)
api_router.include_router(team.router)
