from fastapi import FastAPI
from app.auth.auth_service import router as auth_router
from app.ingestion.ingestion_service import router as ingestion_router

app = FastAPI()

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(ingestion_router, prefix="/ingestion", tags=["ingestion"])

@app.get("/")
def root():
    return {"message": "Welcome to the Cyber Defense Dashboard!"}