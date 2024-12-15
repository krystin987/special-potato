import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def mock_redis_data():
    return {
        b"event:1": {b"event_type": b"LOGIN_ATTEMPT"},
        b"event:2": {b"event_type": b"LOGOUT"},
        b"event:3": {b"event_type": b"LOGIN_ATTEMPT"},
    }

def test_get_event_summary(mock_redis_data, monkeypatch):
    # Mock Redis
    class MockRedis:
        async def keys(self, pattern):
            return list(mock_redis_data.keys())

        async def hgetall(self, key):
            return mock_redis_data[key]

    from app.analytics.analytics_service import redis
    monkeypatch.setattr(redis, "from_url", lambda *args, **kwargs: MockRedis())

    # Call the endpoint
    response = client.get("/analytics/summary")

    # Validate response
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["total_events"] == len(mock_redis_data)
    assert response_data["event_summary"] == {"LOGIN_ATTEMPT": 2, "LOGOUT": 1}