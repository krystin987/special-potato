import redis.asyncio as redis
from fastapi import APIRouter
from sqlalchemy import create_engine, text
from datetime import datetime, timezone

router = APIRouter()

DATABASE_URL = "postgresql://postgres@localhost:5432/cyber_dashboard"
REDIS_HOST = "localhost"
REDIS_PORT = 6379

engine = create_engine(DATABASE_URL)
@router.get("/transform")
async def transform_events():
    return {"message": "Transformation endpoint is working!"}

@router.get("/transform")
async def transform_events():
    # Connect to Redis asynchronously
    redis_client = redis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}")

    # Fetch raw data from PostgreSQL
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, event_type, event_time, data FROM events"))
        events = [dict(row) for row in result]

    # Transform and store data in Redis
    transformed_events = []
    for event in events:
        transformed = {
            "id": event["id"],
            "event_type": event["event_type"].upper(),
            "processed_time": datetime.now(timezone.utc).isoformat(),
            "data": event["data"],
        }
        redis_key = f"event:{event['id']}"
        await redis_client.hset(redis_key, mapping=transformed)
        transformed_events.append(transformed)

    return {"message": "Events transformed and stored in Redis", "transformed_count": len(transformed_events)}