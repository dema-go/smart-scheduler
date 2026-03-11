from sqlalchemy.orm import Session
from datetime import date, timedelta, time, datetime
from typing import List, Dict, Any
from app.models.employee import Employee
from app.models.shift import ShiftType
from app.models.schedule import Schedule


class SchedulerService:
    """智能排班服务"""

    def __init__(self, db: Session):
        self.db = db

    def calculate_shift_duration(self, shift_type: ShiftType) -> float:
        """计算班次时长（小时），考虑跨天情况"""
        start_str = shift_type.start_time
        end_str = shift_type.end_time

        # 解析时间
        start_hour, start_min = map(int, start_str.split(':'))
        end_hour, end_min = map(int, end_str.split(':'))

        start_time = start_hour + start_min / 60
        end_time = end_hour + end_min / 60

        # 计算时长
        if end_time >= start_time:
            # 不跨天
            duration = end_time - start_time
        else:
            # 跨天（如晚班 22:00 - 次日 06:00）
            duration = 24 - start_time + end_time

        return duration

    def get_employee_work_hours(self, employee_id: int, start_date: date, end_date: date) -> float:
        """获取员工在指定日期范围内的总工作时长（小时）"""
        schedules = self.db.query(Schedule).filter(
            Schedule.employee_id == employee_id,
            Schedule.date >= start_date,
            Schedule.date <= end_date
        ).all()

        total_hours = 0.0
        for schedule in schedules:
            shift_type = self.db.query(ShiftType).filter(ShiftType.id == schedule.shift_type_id).first()
            if shift_type:
                total_hours += self.calculate_shift_duration(shift_type)

        return total_hours

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
            # 如果没有设置可用天数，默认所有天都可用
            emp_available_days = emp.available_days if emp.available_days else [0, 1, 2, 3, 4, 5, 6]
            # 检查员工是否在指定日期可用
            if weekday not in emp_available_days:
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
                       existing_hours: Dict[int, float], avg_hours: float = 0,
                       total_employee_count: int = 0, target_hours: float = 0) -> float:
        """计算员工分配到班次的评分"""
        score = 0.0
        shift_duration = self.calculate_shift_duration(shift_type)
        current_hours = existing_hours.get(employee.id, 0.0)

        # 1. 偏好匹配 (权重: 25)
        if shift_type.id in (employee.preferred_shifts or []):
            score += 25

        # 2. 公平性 - 工作时长少的员工优先 (权重: 120)
        # 优化：使用动态目标时长计算，优先分配给未达到目标时长的员工
        if target_hours > 0:
            # 距离目标时长越远，分数越高
            hour_diff = target_hours - current_hours
            score += min(120, max(0, hour_diff * 8))  # 每少1小时加8分，上限120分
        elif avg_hours > 0:
            hour_diff = avg_hours - current_hours
            score += min(120, max(0, hour_diff * 5))
        else:
            score += 50

        # 3. 工作时长均衡 - 严格控制时长差异 (权重: 50)
        # 优化：降低差异容忍度，更严格控制最大时长
        if existing_hours:
            max_hours = max(existing_hours.values())
            min_hours = min(existing_hours.values())
            potential_hours = current_hours + shift_duration

            # 如果分配后超过当前最高时长4小时，扣分
            if potential_hours > max_hours + 4:
                score -= 50
            # 如果分配后超过平均时长太多，也扣分
            elif target_hours > 0 and potential_hours > target_hours + 8:
                score -= 30
            # 如果当前是最低时长，优先分配
            elif current_hours == min_hours and potential_hours <= max_hours:
                score += 20

        # 4. 避免连续同班次 (权重: 10)
        last_shift_id = self.get_employee_last_shift(employee.id, shift_date)
        if last_shift_id == shift_type.id:
            score -= 10  # 连续同班次扣分
        elif last_shift_id != 0:
            score += 5  # 有换班加分

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
        existing_hours: Dict[int, float] = {}  # employee_id -> hours

        # 预计算每个班次的时长
        shift_durations: Dict[int, float] = {
            st.id: self.calculate_shift_duration(st) for st in shift_types
        }

        # 预估总工作时长，用于计算目标工作时长作为评分参考
        days_count = (end_date - start_date).days + 1
        total_shifts_per_day = sum(st.required_count for st in shift_types)
        estimated_total_hours = sum(shift_durations[st.id] * st.required_count for st in shift_types) * days_count
        # 目标时长：总时长除以员工数，得到每个员工应该工作的时长
        target_hours = estimated_total_hours / len(employees) if employees else 0
        avg_hours = target_hours  # 保持向后兼容

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
                            emp, shift_type, current_date, existing_hours, avg_hours,
                            len(employees), target_hours
                        )
                        scored_employees.append((emp, score))

                    # 按评分排序，选择最高分的员工
                    scored_employees.sort(key=lambda x: x[1], reverse=True)

                    if scored_employees:
                        selected_employee = scored_employees[0][0]
                        shift_duration = shift_durations[shift_type.id]

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
                            "date": current_date,
                            "duration": shift_duration
                        })

                        # 更新工作时长统计
                        existing_hours[selected_employee.id] = \
                            existing_hours.get(selected_employee.id, 0.0) + shift_duration

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
