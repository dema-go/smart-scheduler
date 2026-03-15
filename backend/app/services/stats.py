"""
统计服务 - 统一的排班统计逻辑
"""
from sqlalchemy.orm import Session, joinedload
from datetime import date, timedelta
from typing import Dict, List, Any, Optional
from calendar import monthrange

from app.models.employee import Employee
from app.models.shift import ShiftType
from app.models.schedule import Schedule


class StatsService:
    """排班统计服务"""

    def __init__(self, db: Session):
        self.db = db

    def _get_shift_type_cache(self) -> Dict[int, ShiftType]:
        """获取班次类型缓存，避免重复查询"""
        shifts = self.db.query(ShiftType).all()
        return {s.id: s for s in shifts}

    def calculate_shift_duration(self, shift_type: ShiftType) -> float:
        """
        计算班次时长（小时），考虑跨天情况

        Args:
            shift_type: 班次类型对象

        Returns:
            float: 班次时长（小时）
        """
        if not shift_type.start_time or not shift_type.end_time:
            return 0.0

        try:
            start_hour, start_min = map(int, shift_type.start_time.split(':'))
            end_hour, end_min = map(int, shift_type.end_time.split(':'))

            start_time = start_hour + start_min / 60
            end_time = end_hour + end_min / 60

            if end_time >= start_time:
                return end_time - start_time
            else:
                # 跨天班次
                return 24 - start_time + end_time
        except (ValueError, AttributeError):
            return 0.0

    def get_date_range_by_type(
        self,
        stats_type: str,
        year: int,
        month: Optional[int] = None,
        week: Optional[int] = None
    ) -> tuple[date, date]:
        """
        根据统计类型计算日期范围

        Args:
            stats_type: 统计类型 'week' 或 'month'
            year: 年份
            month: 月份（type=month 时必填）
            week: 周数（type=week 时必填）

        Returns:
            tuple: (开始日期, 结束日期)
        """
        if stats_type == "month":
            if month is None:
                raise ValueError("月份统计需要提供 month 参数")
            first_day = date(year, month, 1)
            _, last_day_num = monthrange(year, month)
            last_day = date(year, month, last_day_num)
        elif stats_type == "week":
            if week is None:
                raise ValueError("周统计需要提供 week 参数")
            first_day = date.fromisocalendar(year, week, 1)
            last_day = date.fromisocalendar(year, week, 7)
        else:
            raise ValueError(f"不支持的统计类型: {stats_type}")

        return first_day, last_day

    def get_employee_stats(
        self,
        employee: Employee,
        start_date: date,
        end_date: date,
        schedules: List[Schedule]
    ) -> Dict[str, Any]:
        """
        计算单个员工的排班统计

        Args:
            employee: 员工对象
            start_date: 开始日期
            end_date: 结束日期
            schedules: 该日期范围内的所有排班记录

        Returns:
            dict: 员工统计信息
        """
        # 筛选该员工的排班记录
        emp_schedules = [s for s in schedules if s.employee_id == employee.id]

        # 统计排班天数（按日期去重）
        schedule_dates = set(s.date for s in emp_schedules)

        # 统计班次分布和工作时长
        shift_distribution: Dict[str, int] = {}
        total_hours = 0.0

        for s in emp_schedules:
            if s.shift_type:
                shift_name = s.shift_type.name
                shift_distribution[shift_name] = shift_distribution.get(shift_name, 0) + 1
                total_hours += self.calculate_shift_duration(s.shift_type)

        return {
            "employee_id": employee.id,
            "employee_name": employee.name,
            "total_days": len(schedule_dates),
            "total_hours": round(total_hours, 2),
            "shift_distribution": shift_distribution
        }

    def get_all_employees_stats(
        self,
        start_date: date,
        end_date: date,
        team_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        获取所有员工的排班统计

        Args:
            start_date: 开始日期
            end_date: 结束日期
            team_id: 班组ID（可选，用于筛选）

        Returns:
            list: 员工统计列表
        """
        # 查询员工
        query = self.db.query(Employee).filter(Employee.is_active == True)
        if team_id is not None:
            query = query.filter(Employee.team_id == team_id)
        employees = query.all()

        if not employees:
            return []

        # 查询排班记录（使用 eager loading 避免 N+1 查询）
        schedules = self.db.query(Schedule).options(
            joinedload(Schedule.shift_type),
            joinedload(Schedule.employee)
        ).filter(
            Schedule.date >= start_date,
            Schedule.date <= end_date
        ).all()

        # 计算每个员工的统计
        return [
            self.get_employee_stats(emp, start_date, end_date, schedules)
            for emp in employees
        ]

    def get_employee_work_hours(
        self,
        employee_id: int,
        start_date: date,
        end_date: date
    ) -> float:
        """
        获取员工在指定日期范围内的总工作时长

        Args:
            employee_id: 员工ID
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            float: 总工作时长（小时）
        """
        schedules = self.db.query(Schedule).filter(
            Schedule.employee_id == employee_id,
            Schedule.date >= start_date,
            Schedule.date <= end_date
        ).all()

        return sum(
            self.calculate_shift_duration(s.shift_type)
            for s in schedules
            if s.shift_type
        )
