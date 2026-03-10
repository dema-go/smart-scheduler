from sqlalchemy import Column, Integer, String, Time, Boolean
from sqlalchemy.orm import relationship
from app.models import Base


class ShiftType(Base):
    __tablename__ = "shift_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)  # 班次名称：早班、中班、晚班
    start_time = Column(String(10), nullable=False)  # 开始时间：HH:MM
    end_time = Column(String(10), nullable=False)    # 结束时间：HH:MM
    color = Column(String(20), default="#409EFF")   # 颜色标识
    is_active = Column(Boolean, default=True)
    required_count = Column(Integer, default=1)     # 需要的员工数量

    # 关联
    schedules = relationship("Schedule", back_populates="shift_type")

    def __repr__(self):
        return f"<ShiftType {self.name}>"
