from sqlalchemy import Column, Integer, String, Boolean, JSON, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.models import Base


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    position = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)

    # 可用性：每周可用天数 (0=周一, 6=周日)
    available_days = Column(JSON, default=list)

    # 偏好班次：班次ID列表
    preferred_shifts = Column(JSON, default=list)

    # 可用时间范围
    available_start_time = Column(String(10), nullable=True)
    available_end_time = Column(String(10), nullable=True)

    # 偏好说明
    preference_note = Column(String(500), nullable=True)

    # 班次分配记录
    schedules = relationship("Schedule", back_populates="employee")

    def __repr__(self):
        return f"<Employee {self.name}>"
