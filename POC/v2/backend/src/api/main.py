"""Main entry point for the Navaveij API."""

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

load_dotenv()

from src.api.routes import clinical, contracts, patients
from shared.settings import settings

app = FastAPI(
    title="Navaveij Clinical AI API",
    description="Backend API for clinical recommendations and patient management",
    version="1.0.0",
)

# Configure CORS for Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_allowed_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(patients.router, prefix="/api/v1/patients", tags=["Patients"])
app.include_router(clinical.router, prefix="/api/v1/clinical", tags=["Clinical AI"])
app.include_router(contracts.router, prefix="/api", tags=["Contract API"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}


if __name__ == "__main__":
    logger.info("Starting Navaveij API server...")
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True, reload_dirs=["backend"])
