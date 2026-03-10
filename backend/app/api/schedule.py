from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.models import get_db
from app.models.schedule import Schedule
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate, ScheduleResponse, ScheduleWithDetails
from app.services.scheduler import SchedulerService

router = APIRouter(prefix="/api/schedules", tags=["排班管理"])


@router.get("", response_model=List[ScheduleWithDetails])
def get_schedules(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    employee_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """获取排班列表"""
    query = db.query(Schedule)

    if start_date:
        query = query.filter(Schedule.date >= start_date)
    if end_date:
        query = query.filter(Schedule.date <= end_date)
    if employee_id:
        query = query.filter(Schedule.employee_id == employee_id)

    schedules = query.order_by(Schedule.date).all()

    # 添加详细信息
    result = []
    for s in schedules:
        result.append(ScheduleWithDetails(
            id=s.id,
            employee_id=s.employee_id,
            shift_type_id=s.shift_type_id,
            date=s.date,
            employee_name=s.employee.name if s.employee else "",
            shift_name=s.shift_type.name if s.shift_type else "",
            shift_color=s.shift_type.color if s.shift_type else "#409EFF"
        ))

    return result


@router.get("/{schedule_id}", response_model=ScheduleWithDetails)
def get_schedule(schedule_id: int, db: Session = Depends(get_db)):
    """获取单个排班"""
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="排班不存在")

    return ScheduleWithDetails(
        id=schedule.id,
        employee_id=schedule.employee_id,
        shift_type_id=schedule.shift_type_id,
        date=schedule.date,
        employee_name=schedule.employee.name if schedule.employee else "",
        shift_name=schedule.shift_type.name if schedule.shift_type else "",
        shift_color=schedule.shift_type.color if schedule.shift_type else "#409EFF"
    )


@router.post("", response_model=ScheduleResponse)
def create_schedule(schedule: ScheduleCreate, db: Session = Depends(get_db)):
    """手动创建排班"""
    db_schedule = Schedule(**schedule.model_dump())
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule


@router.put("/{schedule_id}", response_model=ScheduleResponse)
def update_schedule(schedule_id: int, schedule: ScheduleUpdate, db: Session = Depends(get_db)):
    """更新排班"""
    db_schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not db_schedule:
        raise HTTPException(status_code=404, detail="排班不存在")

    for key, value in schedule.model_dump(exclude_unset=True).items():
        setattr(db_schedule, key, value)

    db.commit()
    db.refresh(db_schedule)
    return db_schedule


@router.delete("/{schedule_id}")
def delete_schedule(schedule_id: int, db: Session = Depends(get_db)):
    """删除排班"""
    db_schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not db_schedule:
        raise HTTPException(status_code=404, detail="排班不存在")

    db.delete(db_schedule)
    db.commit()
    return {"message": "排班已删除"}


class GenerateRequest:
    """生成排班请求"""
    start_date: date
    end_date: date


@router.post("/generate")
def generate_schedule(
    start_date: date = Query(...),
    end_date: date = Query(...),
    clear_existing: bool = True,
    db: Session = Depends(get_db)
):
    """生成排班"""
    service = SchedulerService(db)

    # 清除现有排班
    if clear_existing:
        deleted = service.clear_schedule(start_date, end_date)

    # 生成新排班
    schedules = service.generate_schedule(start_date, end_date)

    return {
        "message": f"成功生成 {len(schedules)} 条排班记录",
        "schedules": schedules,
        "deleted": deleted if clear_existing else 0
    }


@router.delete("/clear")
def clear_schedules(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """清除排班"""
    service = SchedulerService(db)
    if not start_date:
        start_date = date.today()
    if not end_date:
        end_date = date.today()

    deleted = service.clear_schedule(start_date, end_date)
    return {"message": f"已清除 {deleted} 条排班记录"}
