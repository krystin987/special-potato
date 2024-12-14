import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def mock_data():
    # Provide mock data for testing if needed
    return [
        {"id": 1, "event_type": "login_attempt", "event_time": "2024-12-14T21:43:30Z", "data": {"user": "johndoe", "success": False, "ip_address": "192.168.1.10"}},
        {"id": 2, "event_type": "logout", "event_time": "2024-12-14T22:00:00Z", "data": {"user": "janedoe", "ip_address": "192.168.1.11"}}
    ]

def test_transform_events(mock_data, monkeypatch):
    # Mock the database connection and execution
    class MockConnection:
        def execute(self, *args, **kwargs):
            class MockResult:
                def __iter__(self):
                    for row in mock_data:
                        yield row
            return MockResult()

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    # Patch the database engine's connect method
    from app.transform.transform_service import engine
    monkeypatch.setattr(engine, "connect", lambda *args: MockConnection())

    # Mock Redis to avoid real calls
    class MockRedis:
        async def hset(self, *args, **kwargs):
            return True

    from app.transform.transform_service import redis
    monkeypatch.setattr(redis, "from_url", lambda *args, **kwargs: MockRedis())

    # Call the endpoint
    response = client.get("/transform/transform")

    # Validate the response
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "Events transformed and stored in Redis"  # Validate the updated message
    assert response_data["transformed_count"] == len(mock_data)  # Validate count matches mock data