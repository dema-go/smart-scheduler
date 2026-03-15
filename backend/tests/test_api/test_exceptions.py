"""
异常处理器测试
"""
import pytest
from fastapi.testclient import TestClient


class TestExceptionHandlers:
    """异常处理器测试类"""

    def test_validation_error_format(self, client):
        """测试验证错误响应格式"""
        # 发送无效数据（缺少必填字段）
        response = client.post("/api/employees", json={})

        assert response.status_code == 422
        data = response.json()
        assert "code" in data
        assert data["code"] == "VALIDATION_ERROR"
        assert "message" in data
        assert "detail" in data
        assert "errors" in data["detail"]

    def test_not_found_error_format(self, client):
        """测试资源不存在响应格式"""
        response = client.get("/api/employees/99999")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_invalid_date_format(self, client):
        """测试无效日期格式"""
        response = client.get("/api/schedules", params={
            "start_date": "invalid-date"
        })

        assert response.status_code == 422
        data = response.json()
        assert data["code"] == "VALIDATION_ERROR"
