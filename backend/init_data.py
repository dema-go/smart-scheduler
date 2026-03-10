"""初始化数据库数据"""
from app.models import SessionLocal, init_db
from app.models.employee import Employee
from app.models.shift import ShiftType


def init_sample_data():
    """初始化示例数据"""
    db = SessionLocal()

    try:
        # 检查是否已有数据
        if db.query(Employee).first():
            print("数据已存在，跳过初始化")
            return

        # 创建班次类型
        shifts = [
            ShiftType(name="早班", start_time="08:00", end_time="16:00", color="#67C23A", required_count=2),
            ShiftType(name="中班", start_time="16:00", end_time="24:00", color="#E6A23C", required_count=2),
            ShiftType(name="晚班", start_time="00:00", end_time="08:00", color="#909399", required_count=1),
        ]
        for shift in shifts:
            db.add(shift)

        # 创建员工
        employees = [
            Employee(
                name="张三",
                position="收银员",
                phone="13800138001",
                email="zhangsan@example.com",
                available_days=[0, 1, 2, 3, 4],
                preferred_shifts=[1]  # 偏好早班
            ),
            Employee(
                name="李四",
                position="售货员",
                phone="13800138002",
                email="lisi@example.com",
                available_days=[1, 2, 3, 4, 5],
                preferred_shifts=[2]  # 偏好中班
            ),
            Employee(
                name="王五",
                position="售货员",
                phone="13800138003",
                email="wangwu@example.com",
                available_days=[0, 2, 4, 6],
                preferred_shifts=[3]  # 偏好晚班
            ),
            Employee(
                name="赵六",
                position="理货员",
                phone="13800138004",
                email="zhaoliu@example.com",
                available_days=[0, 1, 2, 3, 4, 5, 6],
                preferred_shifts=[1, 2]
            ),
            Employee(
                name="孙七",
                position="收银员",
                phone="13800138005",
                email="sunqi@example.com",
                available_days=[2, 3, 4, 5, 6],
                preferred_shifts=[2, 3]
            ),
            Employee(
                name="周八",
                position="店长",
                phone="13800138006",
                email="zhouba@example.com",
                available_days=[0, 5, 6],
                preferred_shifts=[1]
            ),
        ]
        for emp in employees:
            db.add(emp)

        db.commit()
        print("初始化数据成功！")
        print(f"  - 班次类型: {len(shifts)}")
        print(f"  - 员工: {len(employees)}")

    except Exception as e:
        print(f"初始化数据失败: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("初始化数据库...")
    init_db()
    print("数据库初始化完成")

    print("初始化示例数据...")
    init_sample_data()
