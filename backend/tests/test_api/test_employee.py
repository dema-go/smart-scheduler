"""
员工 API 测试
"""
import pytest
from fastapi.testclient import TestClient


class TestEmployeeAPI:
    """员工 API 测试类"""

    def test_create_employee(self, client, sample_employee_data):
        """测试创建员工"""
        response = client.post("/api/employees", json=sample_employee_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_employee_data["name"]
        assert data["position"] == sample_employee_data["position"]
        assert "id" in data

    def test_create_employee_minimal(self, client):
        """测试创建员工 - 最小字段"""
        response = client.post("/api/employees", json={"name": "李四"})
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "李四"

    def test_get_all_employees(self, client, sample_employee_data):
        """测试获取所有员工"""
        # 先创建几个员工
        client.post("/api/employees", json=sample_employee_data)
        client.post("/api/employees", json={**sample_employee_data, "name": "李四"})

        response = client.get("/api/employees")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2

    def test_get_employee_by_id(self, client, sample_employee_data):
        """测试获取单个员工"""
        create_response = client.post("/api/employees", json=sample_employee_data)
        employee_id = create_response.json()["id"]

        response = client.get(f"/api/employees/{employee_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_employee_data["name"]

    def test_get_employee_not_found(self, client):
        """测试获取不存在的员工"""
        response = client.get("/api/employees/99999")
        assert response.status_code == 404

    def test_update_employee(self, client, sample_employee_data):
        """测试更新员工"""
        create_response = client.post("/api/employees", json=sample_employee_data)
        employee_id = create_response.json()["id"]

        update_data = {"name": "王五", "position": "医生"}
        response = client.put(f"/api/employees/{employee_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "王五"
        assert data["position"] == "医生"

    def test_delete_employee(self, client, sample_employee_data):
        """测试删除员工（软删除）"""
        create_response = client.post("/api/employees", json=sample_employee_data)
        employee_id = create_response.json()["id"]

        response = client.delete(f"/api/employees/{employee_id}")
        assert response.status_code == 200
        assert response.json()["message"] == "员工已删除"

        # 验证员工不在列表中（软删除后不显示）
        list_response = client.get("/api/employees")
        employee_ids = [e["id"] for e in list_response.json()]
        assert employee_id not in employee_ids

    def test_update_employee_not_found(self, client):
        """测试更新不存在的员工"""
        response = client.put("/api/employees/99999", json={"name": "测试"})
        assert response.status_code == 404

    def test_delete_employee_not_found(self, client):
        """测试删除不存在的员工"""
        response = client.delete("/api/employees/99999")
        assert response.status_code == 404
