from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from app.models import get_db
from app.models.schedule import Schedule
import csv
import io
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/api/schedules", tags=["排班导出"])


@router.get("/export")
def export_schedules(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    format: str = "csv",
    db: Session = Depends(get_db)
):
    """导出排班数据"""
    query = db.query(Schedule)

    if start_date:
        query = query.filter(Schedule.date >= start_date)
    if end_date:
        query = query.filter(Schedule.date <= end_date)

    schedules = query.order_by(Schedule.date, Schedule.shift_type_id).all()

    # 创建 CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["日期", "员工姓名", "员工职位", "班次", "开始时间", "结束时间", "颜色"])

    for s in schedules:
        writer.writerow([
            s.date.strftime("%Y-%m-%d"),
            s.employee.name if s.employee else "",
            s.employee.position if s.employee else "",
            s.shift_type.name if s.shift_type else "",
            s.shift_type.start_time if s.shift_type else "",
            s.shift_type.end_time if s.shift_type else "",
            s.shift_type.color if s.shift_type else ""
        ])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=schedules_{start_date}_{end_date}.csv"
        }
    )
