"""
SmartPot Waterer API - Mock Mode

This API serves mock data for frontend development.
Arduino communications are disabled in this mode.
"""

import os
import random
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from .models import (
    AirInfo,
    APIError,
    APIStatus,
    AirStatus,
    PlantInfo,
    GroundInfo,
    HealthData,
    APIResponse,
    GroundStatus,
    WateringData,
    WateringRequest,
)

load_dotenv()

# ============================================================================
# Configuration
# ============================================================================

API_VERSION = "1.0.0"
MOCK_MODE = True  # Set to False when Arduino backend is ready

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ============================================================================
# Mock Data Generation
# ============================================================================

def generate_mock_plant_data() -> PlantInfo:
    """Generate realistic mock sensor data for frontend development."""
    temp = round(random.uniform(18.0, 28.0), 1)
    air_humidity = round(random.uniform(40.0, 70.0), 1)
    ground_humidity = round(random.uniform(30.0, 80.0), 1)
    
    # Determine statuses based on values
    if 18 <= temp <= 28 and 40 <= air_humidity <= 70:
        air_status = AirStatus.OPTIMAL
    elif 15 <= temp <= 32 and 30 <= air_humidity <= 80:
        air_status = AirStatus.MODERATE
    else:
        air_status = AirStatus.BAD
    
    ground_status = GroundStatus.OPTIMAL if ground_humidity >= 40 else GroundStatus.DRY
    
    return PlantInfo(
        air=AirInfo(
            temperature=f"{temp}C",
            humidity=f"{air_humidity}%",
            status=air_status
        ),
        ground=GroundInfo(
            humidity=f"{ground_humidity}%",
            status=ground_status
        )
    )


# ============================================================================
# App Initialization
# ============================================================================

app = FastAPI(
    title="SmartPot Waterer API",
    description="API for monitoring and controlling your smart plant watering system. Currently running in MOCK mode for frontend development.",
    version=API_VERSION,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Exception Handlers - Standardized Error Responses
# ============================================================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors with standardized format."""
    errors = exc.errors()
    detail = "; ".join([f"{e['loc'][-1]}: {e['msg']}" for e in errors])
    
    return JSONResponse(
        status_code=422,
        content=APIResponse(
            status=APIStatus.ERROR,
            error=APIError(
                code="VALIDATION_ERROR",
                message="Request validation failed",
                details=detail
            )
        ).model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Catch-all exception handler for unexpected errors."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content=APIResponse(
            status=APIStatus.ERROR,
            error=APIError(
                code="INTERNAL_ERROR",
                message="An unexpected error occurred",
                details=str(exc) if os.getenv("API_ENV") == "dev" else None
            )
        ).model_dump()
    )


# ============================================================================
# Helper Functions
# ============================================================================

def success_response(data) -> APIResponse:
    """Create a standardized success response."""
    return APIResponse(status=APIStatus.SUCCESS, data=data)


def error_response(code: str, message: str, details: str = None) -> APIResponse:
    """Create a standardized error response."""
    return APIResponse(
        status=APIStatus.ERROR,
        error=APIError(code=code, message=message, details=details)
    )


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/health", response_model=APIResponse, tags=["System"])
async def health_check():
    """
    Health check endpoint to verify API is running.
    
    Returns service status, version, and current mode (mock/live).
    """
    return success_response(
        HealthData(
            service="SmartPot API",
            version=API_VERSION,
            mode="mock" if MOCK_MODE else "live"
        ).model_dump()
    )


@app.get("/plant", response_model=APIResponse, tags=["Plant"])
async def get_plant_info():
    """
    Get current plant environment information from sensors.
    
    In mock mode, returns randomized but realistic sensor data.
    
    Response includes:
    - Air temperature and humidity with status (optimal/moderate/bad)
    - Ground humidity with status (optimal/dry)
    """
    if MOCK_MODE:
        plant_data = generate_mock_plant_data()
        logger.info(f"[MOCK] Returning plant data: temp={plant_data.air.temperature}")
        return success_response({"plant_info": plant_data.model_dump()})
    
    # TODO: Implement real Arduino communication when ready
    return error_response(
        code="NOT_IMPLEMENTED",
        message="Live sensor data not yet implemented"
    )


@app.post("/water", response_model=APIResponse, tags=["Control"])
async def trigger_watering(request: WateringRequest = WateringRequest()):
    """
    Manually trigger plant watering.
    
    In mock mode, simulates a successful watering operation.
    
    Parameters:
    - duration_seconds: How long to keep the water valve open (default: 5)
    """
    if request.duration_seconds < 1 or request.duration_seconds > 30:
        return JSONResponse(
            status_code=400,
            content=error_response(
                code="INVALID_DURATION",
                message="Duration must be between 1 and 30 seconds",
                details=f"Received: {request.duration_seconds}"
            ).model_dump()
        )
    
    if MOCK_MODE:
        logger.info(f"[MOCK] Watering triggered for {request.duration_seconds} seconds")
        return success_response(
            WateringData(
                triggered=True,
                duration_seconds=request.duration_seconds,
                message=f"Watering simulated for {request.duration_seconds} seconds"
            ).model_dump()
        )
    
    # TODO: Implement real Arduino communication when ready
    return error_response(
        code="NOT_IMPLEMENTED",
        message="Live watering control not yet implemented"
    )


# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    logger.info("=" * 50)
    logger.info("SmartPot API Starting")
    logger.info(f"Mode: {'MOCK' if MOCK_MODE else 'LIVE'}")
    logger.info("=" * 50)
    
    uvicorn.run(
        "api.src.main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", "8001")),
        reload=os.getenv("API_ENV", "dev") == "dev"
    )
