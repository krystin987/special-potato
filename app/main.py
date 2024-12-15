from fastapi import FastAPI
from app.auth.auth_service import router as auth_router
from app.ingestion.ingestion_service import router as ingestion_router
from app.transform.transform_service import router as transform_router
from app.analytics.analytics_service import router as analytics_router

app = FastAPI()

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(ingestion_router, prefix="/ingestion", tags=["ingestion"])
app.include_router(transform_router, prefix="/transform", tags=["transform"])
app.include_router(analytics_router, prefix="/analytics", tags=["analytics"])

@app.get("/")
def root():
    return {"message": "Welcome to the Cyber Defense Dashboard!"}