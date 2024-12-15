from fastapi import APIRouter, HTTPException
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, JSON, DateTime, text
import json
from pydantic import BaseModel, Field
import logging
import os

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)
# Define the router
router = APIRouter()

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set. Check your .env file.")
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

# Define the schema for the event payload
class Event(BaseModel):
    event_type: str = Field(..., description="Type of the event")
    event_time: str = Field(..., description="Timestamp of the event in ISO format")
    data: dict = Field(..., description="Additional data related to the event")

SessionLocal = sessionmaker(bind=engine)

@router.post("/ingest")
async def ingest_event(event: Event):
    try:
        validated_event = event.model_dump()
        validated_event["data"] = json.dumps(validated_event["data"])  # Serialize data to JSON string

        with engine.connect() as conn:
            conn.execute(
                text(
                    """
                    INSERT INTO events (event_type, event_time, data)
                    VALUES (:event_type, :event_time, :data)
                    """
                ),
                validated_event,
            )
        return {
            "message": "Event ingested successfully",
            "event_time": validated_event["event_time"]
        }
    except IntegrityError as e:
        logger.error(f"Integrity error during ingestion: {e}")
        raise HTTPException(status_code=409, detail="Duplicate event detected")
    except Exception as e:
        logger.error(f"Error during ingestion: {e}")
        raise HTTPException(status_code=500, detail="Database error")