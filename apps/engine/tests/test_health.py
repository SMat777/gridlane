from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "gridlane-engine"


def test_health_includes_version():
    response = client.get("/api/v1/health")
    data = response.json()
    assert "version" in data
