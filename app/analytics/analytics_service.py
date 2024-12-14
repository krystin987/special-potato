from fastapi import APIRouter
import redis.asyncio as redis

router = APIRouter()

REDIS_HOST = "localhost"
REDIS_PORT = 6379

@router.get("/summary")
async def get_event_summary():
    # Connect to Redis
    redis_client = redis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}")

    # Fetch all keys
    keys = await redis_client.keys("event:*")

    # Aggregate event types
    event_summary = {}
    for key in keys:
        event = await redis_client.hgetall(key)
        event_type = event.get(b"event_type", b"UNKNOWN").decode("utf-8")
        event_summary[event_type] = event_summary.get(event_type, 0) + 1

    return {"total_events": len(keys), "event_summary": event_summary}