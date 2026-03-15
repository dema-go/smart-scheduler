"""
排班算法测试
"""
import pytest
from datetime import date, timedelta
from sqlalchemy.orm import Session

from app.services.scheduler import SchedulerService
from app.models.employee import Employee
from app.models.shift import ShiftType
from app.models.schedule import Schedule
from app.models.team import Team


class TestSchedulerService:
    """排班算法测试类"""

    @pytest.fixture
    def setup_data(self, db_session):
        """准备测试数据"""
        # 创建班组
        team = Team(name="测试班组", description="测试用")
        db_session.add(team)
        db_session.commit()

        # 创建员工
        employees = []
        for i in range(5):
            emp = Employee(
                name=f"员工{i+1}",
                position="护士",
                is_active=True,
                team_id=team.id,
                available_days=[0, 1, 2, 3, 4, 5, 6],  # 每天都可用
                preferred_shifts=[]
            )
            db_session.add(emp)
            employees.append(emp)
        db_session.commit()

        # 创建班次
        shifts = []
        shift_configs = [
            ("早班", "08:00", "16:00", "#409EFF", 2),
            ("中班", "14:00", "22:00", "#67C23A", 1),
            ("晚班", "22:00", "06:00", "#E6A23C", 1),
        ]
        for name, start, end, color, count in shift_configs:
            shift = ShiftType(
                name=name,
                start_time=start,
                end_time=end,
                color=color,
                required_count=count,
                is_active=True
            )
            db_session.add(shift)
            shifts.append(shift)
        db_session.commit()

        return {
            "team": team,
            "employees": employees,
            "shifts": shifts
        }

    def test_calculate_shift_duration_normal(self, db_session, setup_data):
        """测试计算普通班次时长"""
        service = SchedulerService(db_session)
        shift = setup_data["shifts"][0]  # 早班 08:00-16:00

        duration = service.calculate_shift_duration(shift)
        assert duration == 8.0

    def test_calculate_shift_duration_overnight(self, db_session, setup_data):
        """测试计算跨天班次时长"""
        service = SchedulerService(db_session)
        shift = setup_data["shifts"][2]  # 晚班 22:00-06:00

        duration = service.calculate_shift_duration(shift)
        assert duration == 8.0  # 跨天 8 小时

    def test_get_available_employees(self, db_session, setup_data):
        """测试获取可用员工"""
        service = SchedulerService(db_session)
        shift = setup_data["shifts"][0]
        test_date = date(2024, 1, 8)  # 周一

        available = service.get_available_employees(shift, test_date)
        assert len(available) == 5  # 所有员工都可用

    def test_get_available_employees_with_existing_schedule(self, db_session, setup_data):
        """测试已排班员工不可用"""
        service = SchedulerService(db_session)
        shift = setup_data["shifts"][0]
        test_date = date(2024, 1, 8)

        # 给第一个员工排班
        schedule = Schedule(
            employee_id=setup_data["employees"][0].id,
            shift_type_id=shift.id,
            date=test_date
        )
        db_session.add(schedule)
        db_session.commit()

        available = service.get_available_employees(shift, test_date)
        assert len(available) == 4  # 少了一个

    def test_get_available_employees_by_weekday(self, db_session, setup_data):
        """测试按星期筛选可用员工"""
        service = SchedulerService(db_session)

        # 修改员工可用天数为只周一到周五
        for emp in setup_data["employees"]:
            emp.available_days = [0, 1, 2, 3, 4]
        db_session.commit()

        shift = setup_data["shifts"][0]

        # 周一应该可用
        available_monday = service.get_available_employees(shift, date(2024, 1, 8))
        assert len(available_monday) == 5

        # 周日应该不可用
        available_sunday = service.get_available_employees(shift, date(2024, 1, 7))
        assert len(available_sunday) == 0

    def test_generate_schedule_basic(self, db_session, setup_data):
        """测试基本排班生成"""
        service = SchedulerService(db_session)

        start_date = date(2024, 1, 8)  # 周一
        end_date = date(2024, 1, 14)   # 周日

        schedules = service.generate_schedule(start_date, end_date)

        # 7天 * (2早班 + 1中班 + 1晚班) = 28 条排班
        assert len(schedules) == 28

    def test_generate_schedule_with_team_filter(self, db_session, setup_data):
        """测试按班组生成排班"""
        service = SchedulerService(db_session)

        # 创建另一个班组的员工
        other_team = Team(name="其他班组", description="其他")
        db_session.add(other_team)
        db_session.commit()

        other_emp = Employee(
            name="其他员工",
            position="护士",
            is_active=True,
            team_id=other_team.id,
            available_days=[0, 1, 2, 3, 4, 5, 6]
        )
        db_session.add(other_emp)
        db_session.commit()

        start_date = date(2024, 1, 8)
        end_date = date(2024, 1, 14)

        # 只为测试班组排班
        schedules = service.generate_schedule(
            start_date, end_date,
            team_id=setup_data["team"].id
        )

        # 验证所有排班都属于测试班组
        for s in schedules:
            emp = db_session.query(Employee).filter(
                Employee.id == s["employee_id"]
            ).first()
            assert emp.team_id == setup_data["team"].id

    def test_schedule_fairness(self, db_session, setup_data):
        """测试排班公平性"""
        service = SchedulerService(db_session)

        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)  # 一个月

        schedules = service.generate_schedule(start_date, end_date)

        # 统计每个员工的排班次数
        employee_counts = {}
        for s in schedules:
            emp_id = s["employee_id"]
            employee_counts[emp_id] = employee_counts.get(emp_id, 0) + 1

        # 计算最大最小差异
        counts = list(employee_counts.values())
        max_count = max(counts)
        min_count = min(counts)

        # 差异不应超过 3 天（允许一定不均衡）
        assert max_count - min_count <= 3, f"排班不公平: 最多{max_count}, 最少{min_count}"

    def test_schedule_respects_preferred_shifts(self, db_session, setup_data):
        """测试排班偏好"""
        # 设置员工1偏好早班
        setup_data["employees"][0].preferred_shifts = [setup_data["shifts"][0].id]
        db_session.commit()

        service = SchedulerService(db_session)

        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)

        schedules = service.generate_schedule(start_date, end_date)

        # 统计员工1的班次分布
        emp1_shifts = {}
        for s in schedules:
            if s["employee_id"] == setup_data["employees"][0].id:
                shift_name = s["shift_name"]
                emp1_shifts[shift_name] = emp1_shifts.get(shift_name, 0) + 1

        # 早班应该是最多的（因为有偏好加分）
        assert emp1_shifts.get("早班", 0) >= emp1_shifts.get("晚班", 0)

    def test_clear_schedule(self, db_session, setup_data):
        """测试清除排班"""
        service = SchedulerService(db_session)

        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 7)

        # 生成排班
        service.generate_schedule(start_date, end_date)

        # 清除排班
        deleted = service.clear_schedule(start_date, end_date)

        assert deleted > 0

        # 验证已清除
        remaining = db_session.query(Schedule).filter(
            Schedule.date >= start_date,
            Schedule.date <= end_date
        ).count()
        assert remaining == 0
