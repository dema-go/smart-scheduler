from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.models import Base


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)

    # 关联员工
    employees = relationship("Employee", back_populates="team")

    def __repr__(self):
        return f"<Team {self.name}>"
