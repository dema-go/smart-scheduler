from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.models import Base


class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    shift_type_id = Column(Integer, ForeignKey("shift_types.id"), nullable=False)
    date = Column(Date, nullable=False)  # 排班日期

    # 关联
    employee = relationship("Employee", back_populates="schedules")
    shift_type = relationship("ShiftType", back_populates="schedules")

    def __repr__(self):
        return f"<Schedule {self.employee_id} - {self.shift_type_id} on {self.date}>"
