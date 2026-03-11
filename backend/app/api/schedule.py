from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Any
from datetime import date
from calendar import monthrange
from app.models import get_db
from app.models.schedule import Schedule
from app.models.employee import Employee
from app.models.shift import ShiftType
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


@router.get("/stats")
def get_schedule_stats(
    year: int = Query(..., description="年份"),
    month: int = Query(..., ge=1, le=12, description="月份"),
    db: Session = Depends(get_db)
):
    """获取员工排班统计"""
    try:
        # 计算月份的第一天和最后一天
        first_day = date(year, month, 1)
        _, last_day_num = monthrange(year, month)
        last_day = date(year, month, last_day_num)

        # 获取所有员工
        employees = db.query(Employee).filter(Employee.is_active == True).all()
        if not employees:
            return {"year": year, "month": month, "employees": []}

        # 获取该月所有排班记录
        schedules = db.query(Schedule).filter(
            Schedule.date >= first_day,
            Schedule.date <= last_day
        ).all()

        # 构建员工排班统计
        employee_stats = []
        for emp in employees:
            # 该员工的排班记录
            emp_schedules = [s for s in schedules if s.employee_id == emp.id]

            # 统计排班天数（按日期去重）
            schedule_dates = set(s.date for s in emp_schedules)

            # 统计班次分布
            shift_distribution = {}
            for s in emp_schedules:
                shift_name = s.shift_type.name if s.shift_type else "未知"
                shift_distribution[shift_name] = shift_distribution.get(shift_name, 0) + 1

            employee_stats.append({
                "employee_id": emp.id,
                "employee_name": emp.name,
                "total_days": len(schedule_dates),
                "shift_distribution": shift_distribution
            })

        return {
            "year": year,
            "month": month,
            "employees": employee_stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计数据失败: {str(e)}")


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


@router.post("/batch-delete")
def batch_delete_schedules(
    ids: List[int],
    db: Session = Depends(get_db)
):
    """批量删除排班"""
    if not ids:
        raise HTTPException(status_code=400, detail="请提供要删除的排班ID列表")

    # 查询所有要删除的排班
    schedules = db.query(Schedule).filter(Schedule.id.in_(ids)).all()

    if not schedules:
        raise HTTPException(status_code=404, detail="未找到指定的排班记录")

    deleted_count = len(schedules)

    # 批量删除
    for schedule in schedules:
        db.delete(schedule)

    db.commit()

    return {
        "message": f"成功删除 {deleted_count} 条排班记录",
        "deleted_count": deleted_count
    }


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

