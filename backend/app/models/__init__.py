from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.config import settings

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """SQLAlchemy 2.0 风格的基类"""
    pass


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库"""
    # 导入所有模型类，确保 relationship 字符串引用能正确解析
    from app.models.employee import Employee
    from app.models.shift import ShiftType
    from app.models.schedule import Schedule
    from app.models.team import Team
    Base.metadata.create_all(bind=engine)
