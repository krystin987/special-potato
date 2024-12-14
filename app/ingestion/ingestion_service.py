from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, JSON, DateTime
from sqlalchemy.sql import insert
import datetime

# Define the router
router = APIRouter()

# Database connection
# DATABASE_URL = "postgresql://postgres:@localhost:5432/cyber_dashboard"
DATABASE_URL = "postgresql://postgres@localhost:5432/cyber_dashboard"
engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    print("Connection successful!")

engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Define the events table
events = Table(
    "events",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("event_type", String(50), nullable=False),
    Column("event_time", DateTime, nullable=False),
    Column("data", JSON, nullable=False)
)

metadata.create_all(engine)

# Pydantic model for event data
class Event(BaseModel):
    event_type: str
    data: dict

@router.post("/ingest")
async def ingest_event(event: Event):
    # Prepare the event data
    event_time = datetime.datetime.utcnow()
    query = insert(events).values(
        event_type=event.event_type,
        event_time=event_time,
        data=event.data
    )
    with engine.connect() as conn:
        try:
            conn.execute(query)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {e}")
    return {"message": "Event ingested successfully", "event_time": event_time}