from sqlalchemy.orm import Session
from datetime import date, timedelta
from typing import List, Dict, Any
from app.models.employee import Employee
from app.models.shift import ShiftType
from app.models.schedule import Schedule


class SchedulerService:
    """智能排班服务"""

    def __init__(self, db: Session):
        self.db = db

    def get_employee_schedule_count(self, employee_id: int, start_date: date, end_date: date) -> int:
        """获取员工在指定日期范围内的排班次数"""
        return self.db.query(Schedule).filter(
            Schedule.employee_id == employee_id,
            Schedule.date >= start_date,
            Schedule.date <= end_date
        ).count()

    def get_employee_last_shift(self, employee_id: int, before_date: date) -> int:
        """获取员工在指定日期之前的最后一个班次"""
        last_schedule = self.db.query(Schedule).filter(
            Schedule.employee_id == employee_id,
            Schedule.date < before_date
        ).order_by(Schedule.date.desc()).first()

        return last_schedule.shift_type_id if last_schedule else 0

    def get_available_employees(self, shift_type: ShiftType, shift_date: date) -> List[Employee]:
        """获取可用的员工列表"""
        # 获取所有活跃员工
        all_employees = self.db.query(Employee).filter(Employee.is_active == True).all()

        # 获取指定日期的星期几 (0=周一, 6=周日)
        weekday = shift_date.weekday()

        available = []
        for emp in all_employees:
            # 检查员工是否在指定日期可用
            if weekday not in (emp.available_days or []):
                continue
            # 检查员工是否已有该日期的排班
            existing = self.db.query(Schedule).filter(
                Schedule.employee_id == emp.id,
                Schedule.date == shift_date
            ).first()
            if existing:
                continue
            available.append(emp)

        return available

    def calculate_score(self, employee: Employee, shift_type: ShiftType, shift_date: date,
                       existing_schedules: Dict[int, int]) -> float:
        """计算员工分配到班次的评分"""
        score = 0.0

        # 1. 偏好匹配 (权重: 40)
        if shift_type.id in (employee.preferred_shifts or []):
            score += 40

        # 2. 公平性 - 班次少的员工优先 (权重: 40)
        current_count = existing_schedules.get(employee.id, 0)
        score += max(0, 40 - current_count * 5)

        # 3. 避免连续同班次 (权重: 20)
        last_shift_id = self.get_employee_last_shift(employee.id, shift_date)
        if last_shift_id == shift_type.id:
            score -= 20  # 连续同班次扣分
        elif last_shift_id != 0:
            score += 10  # 有换班加分

        return score

    def generate_schedule(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """生成排班"""
        # 获取所有活跃的班次类型
        shift_types = self.db.query(ShiftType).filter(ShiftType.is_active == True).all()
        if not shift_types:
            return []

        # 获取所有活跃的员工
        employees = self.db.query(Employee).filter(Employee.is_active == True).all()
        if not employees:
            return []

        # 记录已生成的排班
        schedules_created = []
        existing_schedules: Dict[int, int] = {}  # employee_id -> count

        # 遍历日期范围
        current_date = start_date
        while current_date <= end_date:
            # 遍历每个班次类型
            for shift_type in shift_types:
                # 需要分配的人数
                for _ in range(shift_type.required_count):
                    # 获取可用员工
                    available_employees = self.get_available_employees(shift_type, current_date)
                    if not available_employees:
                        continue

                    # 计算每个员工的评分
                    scored_employees = []
                    for emp in available_employees:
                        score = self.calculate_score(
                            emp, shift_type, current_date, existing_schedules
                        )
                        scored_employees.append((emp, score))

                    # 按评分排序，选择最高分的员工
                    scored_employees.sort(key=lambda x: x[1], reverse=True)

                    if scored_employees:
                        selected_employee = scored_employees[0][0]

                        # 创建排班记录
                        schedule = Schedule(
                            employee_id=selected_employee.id,
                            shift_type_id=shift_type.id,
                            date=current_date
                        )
                        self.db.add(schedule)
                        schedules_created.append({
                            "employee_id": selected_employee.id,
                            "employee_name": selected_employee.name,
                            "shift_type_id": shift_type.id,
                            "shift_name": shift_type.name,
                            "date": current_date
                        })

                        # 更新计数
                        existing_schedules[selected_employee.id] = \
                            existing_schedules.get(selected_employee.id, 0) + 1

            current_date += timedelta(days=1)

        # 提交所有排班
        self.db.commit()

        return schedules_created

    def clear_schedule(self, start_date: date, end_date: date) -> int:
        """清除指定日期范围内的排班"""
        deleted = self.db.query(Schedule).filter(
            Schedule.date >= start_date,
            Schedule.date <= end_date
        ).delete()
        self.db.commit()
        return deleted
