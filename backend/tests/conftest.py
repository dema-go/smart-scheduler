"""
测试配置和 fixtures
"""
import pytest
import tempfile
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.models import Base, get_db


# 使用内存数据库进行测试
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """测试用的数据库依赖"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db_session():
    """创建测试数据库会话"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """创建测试客户端"""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def sample_employee_data():
    """示例员工数据"""
    return {
        "name": "张三",
        "position": "护士",
        "phone": "13800138000",
        "email": "zhangsan@example.com",
        "is_active": True,
        "available_days": [0, 1, 2, 3, 4],  # 周一到周五
        "preferred_shifts": []
    }


@pytest.fixture
def sample_shift_data():
    """示例班次数据"""
    return {
        "name": "早班",
        "start_time": "08:00",
        "end_time": "16:00",
        "color": "#409EFF",
        "required_count": 2,
        "is_active": True
    }


@pytest.fixture
def sample_team_data():
    """示例班组数据"""
    return {
        "name": "护理一组",
        "description": "负责A区护理工作"
    }
