"""
SmartPot Waterer API

Reads sensor data from JSON file (populated by arduino_daemon.py)
Sends commands via command file (processed by arduino_daemon.py)
"""

import os
import json
import time
import logging
from pathlib import Path
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
MOCK_MODE = os.getenv("MOCK_MODE", "false").lower() == "true"

# Data file paths
SCRIPT_DIR = Path(__file__).parent.parent  # api/
DATA_DIR = SCRIPT_DIR / "data"
SENSOR_FILE = DATA_DIR / "sensor_data.json"
COMMAND_FILE = DATA_DIR / "command.txt"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ============================================================================
# Data Access Functions
# ============================================================================

def read_sensor_data() -> dict | None:
    """Read current sensor data from JSON file."""
    if not SENSOR_FILE.exists():
        return None
    
    try:
        with open(SENSOR_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Failed to read sensor data: {e}")
        return None


def send_command(command: str) -> bool:
    """Write command to file for daemon to process."""
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(COMMAND_FILE, "w") as f:
            f.write(command)
        return True
    except IOError as e:
        logger.error(f"Failed to write command: {e}")
        return False


def build_plant_info(data: dict) -> PlantInfo:
    """Convert raw sensor data to PlantInfo model."""
    temp = data.get("temperature")
    air_hum = data.get("air_humidity")
    soil_hum = data.get("soil_humidity")
    
    # Map status strings to enums
    air_status_map = {
        "optimal": AirStatus.OPTIMAL,
        "moderate": AirStatus.MODERATE,
        "bad": AirStatus.BAD
    }
    ground_status_map = {
        "optimal": GroundStatus.OPTIMAL,
        "dry": GroundStatus.DRY
    }
    
    air_status = air_status_map.get(data.get("air_status", ""), AirStatus.MODERATE)
    ground_status = ground_status_map.get(data.get("ground_status", ""), GroundStatus.DRY)
    
    return PlantInfo(
        air=AirInfo(
            temperature=f"{temp}C" if temp is not None else "--C",
            humidity=f"{air_hum}%" if air_hum is not None else "--%",
            status=air_status
        ),
        ground=GroundInfo(
            humidity=f"{soil_hum}%" if soil_hum is not None else "--%",
            status=ground_status
        )
    )


# ============================================================================
# App Initialization
# ============================================================================

app = FastAPI(
    title="SmartPot Waterer API",
    description="API for monitoring and controlling your smart plant watering system.",
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
# Exception Handlers
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
    """Health check endpoint to verify API is running."""
    sensor_data = read_sensor_data()
    daemon_status = sensor_data.get("daemon_status", "unknown") if sensor_data else "no_data"
    
    return success_response(
        HealthData(
            service="SmartPot API",
            version=API_VERSION,
            mode="mock" if MOCK_MODE else "live",
        ).model_dump() | {"daemon_status": daemon_status}
    )


@app.get("/plant", response_model=APIResponse, tags=["Plant"])
async def get_plant_info():
    """
    Get current plant environment information from sensors.
    
    Reads from sensor_data.json (populated by arduino_daemon).
    """
    sensor_data = read_sensor_data()
    
    if sensor_data and sensor_data.get("temperature") is not None:
        plant_info = build_plant_info(sensor_data)
        return success_response({
            "plant_info": plant_info.model_dump(),
            "last_updated": sensor_data.get("last_updated")
        })
    
    # No data available
    return JSONResponse(
        status_code=503,
        content=error_response(
            code="NO_SENSOR_DATA",
            message="Sensor data not available",
            details="Arduino daemon may not be running or connected"
        ).model_dump()
    )


@app.post("/water", response_model=APIResponse, tags=["Control"])
async def trigger_watering(request: WateringRequest = WateringRequest()):
    """
    Manually trigger plant watering.
    
    Sends 'go' command to Arduino via daemon.
    For duration > 0, sends 'go' to open, waits, sends 'go' to close.
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
    
    # Send "go" to open valve
    if not send_command("go"):
        return JSONResponse(
            status_code=503,
            content=error_response(
                code="COMMAND_FAILED",
                message="Failed to send command to Arduino"
            ).model_dump()
        )
    
    logger.info(f"Watering started for {request.duration_seconds} seconds")
    
    # Wait for duration
    time.sleep(request.duration_seconds)
    
    # Send "go" again to close valve
    if not send_command("go"):
        logger.warning("Failed to send close command")
    
    logger.info("Watering completed")
    
    return success_response(
        WateringData(
            triggered=True,
            duration_seconds=request.duration_seconds,
            message=f"Watering completed for {request.duration_seconds} seconds"
        ).model_dump()
    )


# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    logger.info("=" * 50)
    logger.info("SmartPot API Starting")
    logger.info(f"Mode: {'MOCK' if MOCK_MODE else 'LIVE'}")
    logger.info(f"Sensor file: {SENSOR_FILE}")
    logger.info("=" * 50)
    
    uvicorn.run(
        "api.src.main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", "8001")),
        reload=os.getenv("API_ENV", "dev") == "dev"
    )
