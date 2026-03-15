"""
班组 API 测试
"""
import pytest


class TestTeamAPI:
    """班组 API 测试类"""

    def test_create_team(self, client, sample_team_data):
        """测试创建班组"""
        response = client.post("/api/teams", json=sample_team_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_team_data["name"]
        assert data["description"] == sample_team_data["description"]
        assert "id" in data

    def test_get_all_teams(self, client, sample_team_data):
        """测试获取所有班组"""
        client.post("/api/teams", json=sample_team_data)
        client.post("/api/teams", json={**sample_team_data, "name": "护理二组"})

        response = client.get("/api/teams")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2

    def test_get_team_by_id(self, client, sample_team_data):
        """测试获取单个班组"""
        create_response = client.post("/api/teams", json=sample_team_data)
        team_id = create_response.json()["id"]

        response = client.get(f"/api/teams/{team_id}")
        assert response.status_code == 200
        assert response.json()["name"] == sample_team_data["name"]

    def test_update_team(self, client, sample_team_data):
        """测试更新班组"""
        create_response = client.post("/api/teams", json=sample_team_data)
        team_id = create_response.json()["id"]

        update_data = {"name": "护理二组", "description": "负责B区"}
        response = client.put(f"/api/teams/{team_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "护理二组"

    def test_delete_team(self, client, sample_team_data):
        """测试删除班组"""
        create_response = client.post("/api/teams", json=sample_team_data)
        team_id = create_response.json()["id"]

        response = client.delete(f"/api/teams/{team_id}")
        assert response.status_code == 200

        # 验证已删除
        get_response = client.get(f"/api/teams/{team_id}")
        assert get_response.status_code == 404

    def test_team_not_found(self, client):
        """测试获取不存在的班组"""
        response = client.get("/api/teams/99999")
        assert response.status_code == 404
