"""
班次 API 测试
"""
import pytest


class TestShiftAPI:
    """班次 API 测试类"""

    def test_create_shift(self, client, sample_shift_data):
        """测试创建班次"""
        response = client.post("/api/shifts", json=sample_shift_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_shift_data["name"]
        assert data["start_time"] == sample_shift_data["start_time"]
        assert data["end_time"] == sample_shift_data["end_time"]
        assert "id" in data

    def test_create_shift_minimal(self, client):
        """测试创建班次 - 最小字段"""
        response = client.post("/api/shifts", json={
            "name": "晚班",
            "start_time": "16:00",
            "end_time": "00:00"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "晚班"

    def test_get_all_shifts(self, client, sample_shift_data):
        """测试获取所有班次"""
        client.post("/api/shifts", json=sample_shift_data)
        client.post("/api/shifts", json={**sample_shift_data, "name": "晚班"})

        response = client.get("/api/shifts")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2

    def test_get_shift_by_id(self, client, sample_shift_data):
        """测试获取单个班次"""
        create_response = client.post("/api/shifts", json=sample_shift_data)
        shift_id = create_response.json()["id"]

        response = client.get(f"/api/shifts/{shift_id}")
        assert response.status_code == 200
        assert response.json()["name"] == sample_shift_data["name"]

    def test_update_shift(self, client, sample_shift_data):
        """测试更新班次"""
        create_response = client.post("/api/shifts", json=sample_shift_data)
        shift_id = create_response.json()["id"]

        # 更新时需要包含所有必要字段
        update_data = {
            "name": "上午班",
            "start_time": "06:00",
            "end_time": "14:00",
            "required_count": 3
        }
        response = client.put(f"/api/shifts/{shift_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "上午班"
        assert data["required_count"] == 3

    def test_delete_shift(self, client, sample_shift_data):
        """测试删除班次（软删除）"""
        create_response = client.post("/api/shifts", json=sample_shift_data)
        shift_id = create_response.json()["id"]

        response = client.delete(f"/api/shifts/{shift_id}")
        assert response.status_code == 200
        assert response.json()["message"] == "班次类型已删除"

        # 验证班次不在列表中（软删除后不显示）
        list_response = client.get("/api/shifts")
        shift_ids = [s["id"] for s in list_response.json()]
        assert shift_id not in shift_ids

    def test_shift_not_found(self, client):
        """测试获取不存在的班次"""
        response = client.get("/api/shifts/99999")
        assert response.status_code == 404
