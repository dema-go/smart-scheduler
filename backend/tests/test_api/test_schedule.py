"""
排班 API 测试
"""
import pytest
from datetime import date, timedelta


class TestScheduleAPI:
    """排班 API 测试类"""

    @pytest.fixture(autouse=True)
    def setup_data(self, client, sample_employee_data, sample_shift_data, sample_team_data):
        """每个测试前准备数据"""
        # 创建班组
        team_response = client.post("/api/teams", json=sample_team_data)
        self.team_id = team_response.json()["id"]

        # 更新员工数据，关联班组
        employee_with_team = {**sample_employee_data, "team_id": self.team_id}

        # 创建员工
        emp1 = client.post("/api/employees", json=employee_with_team).json()
        emp2 = client.post("/api/employees", json={**employee_with_team, "name": "李四"}).json()
        self.employee_ids = [emp1["id"], emp2["id"]]

        # 创建班次
        shift1 = client.post("/api/shifts", json=sample_shift_data).json()
        shift2 = client.post("/api/shifts", json={
            **sample_shift_data,
            "name": "晚班",
            "start_time": "16:00",
            "end_time": "00:00"
        }).json()
        self.shift_ids = [shift1["id"], shift2["id"]]

    def test_create_schedule(self, client):
        """测试创建排班"""
        schedule_data = {
            "employee_id": self.employee_ids[0],
            "shift_type_id": self.shift_ids[0],
            "date": str(date.today())
        }
        response = client.post("/api/schedules", json=schedule_data)
        assert response.status_code == 200
        data = response.json()
        assert data["employee_id"] == self.employee_ids[0]
        assert data["shift_type_id"] == self.shift_ids[0]

    def test_get_schedules_paginated(self, client):
        """测试分页获取排班列表"""
        # 创建几条排班
        today = date.today()
        for i in range(3):
            client.post("/api/schedules", json={
                "employee_id": self.employee_ids[i % 2],
                "shift_type_id": self.shift_ids[i % 2],
                "date": str(today + timedelta(days=i))
            })

        response = client.get("/api/schedules", params={"page": 1, "page_size": 2})
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert data["page"] == 1
        assert data["page_size"] == 2

    def test_get_schedules_by_date_range(self, client):
        """测试按日期范围筛选排班"""
        today = date.today()
        # 创建不同日期的排班
        client.post("/api/schedules", json={
            "employee_id": self.employee_ids[0],
            "shift_type_id": self.shift_ids[0],
            "date": str(today)
        })
        client.post("/api/schedules", json={
            "employee_id": self.employee_ids[1],
            "shift_type_id": self.shift_ids[0],
            "date": str(today + timedelta(days=10))
        })

        response = client.get("/api/schedules", params={
            "start_date": str(today),
            "end_date": str(today + timedelta(days=5))
        })
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1

    def test_update_schedule(self, client):
        """测试更新排班"""
        create_response = client.post("/api/schedules", json={
            "employee_id": self.employee_ids[0],
            "shift_type_id": self.shift_ids[0],
            "date": str(date.today())
        })
        schedule_id = create_response.json()["id"]

        update_data = {
            "employee_id": self.employee_ids[1],
            "shift_type_id": self.shift_ids[1]
        }
        response = client.put(f"/api/schedules/{schedule_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["employee_id"] == self.employee_ids[1]

    def test_delete_schedule(self, client):
        """测试删除排班"""
        create_response = client.post("/api/schedules", json={
            "employee_id": self.employee_ids[0],
            "shift_type_id": self.shift_ids[0],
            "date": str(date.today())
        })
        schedule_id = create_response.json()["id"]

        response = client.delete(f"/api/schedules/{schedule_id}")
        assert response.status_code == 200

        # 验证已删除
        get_response = client.get(f"/api/schedules/{schedule_id}")
        assert get_response.status_code == 404

    def test_batch_delete_schedules(self, client):
        """测试批量删除排班"""
        # 创建多条排班
        ids = []
        today = date.today()
        for i in range(3):
            response = client.post("/api/schedules", json={
                "employee_id": self.employee_ids[i % 2],
                "shift_type_id": self.shift_ids[0],
                "date": str(today + timedelta(days=i))
            })
            ids.append(response.json()["id"])

        response = client.post("/api/schedules/batch-delete", json=ids)
        assert response.status_code == 200
        data = response.json()
        assert data["deleted_count"] == 3

    def test_generate_schedule(self, client):
        """测试生成排班"""
        today = date.today()
        response = client.post("/api/schedules/generate", params={
            "start_date": str(today),
            "end_date": str(today + timedelta(days=3)),
            "clear_existing": True
        })
        assert response.status_code == 200
        data = response.json()
        assert "schedules" in data
        assert len(data["schedules"]) > 0

    def test_get_schedule_stats(self, client):
        """测试获取排班统计"""
        # 先生成一些排班
        today = date.today()
        client.post("/api/schedules/generate", params={
            "start_date": str(today.replace(day=1)),
            "end_date": str(today),
            "clear_existing": True
        })

        response = client.get("/api/schedules/stats", params={
            "type": "month",
            "year": today.year,
            "month": today.month
        })
        assert response.status_code == 200
        data = response.json()
        assert "employees" in data
        assert "year" in data
        assert "month" in data
