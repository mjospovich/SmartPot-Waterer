from enum import Enum
from pydantic import BaseModel
from typing import Any, Optional


# ============================================================================
# Standard API Response Models
# ============================================================================

class APIStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"


class APIError(BaseModel):
    """Standardized error detail."""
    code: str
    message: str
    details: Optional[str] = None


class APIResponse(BaseModel):
    """
    Standardized API response wrapper.
    All endpoints return this structure for consistency.
    """
    status: APIStatus
    data: Optional[Any] = None
    error: Optional[APIError] = None


# ============================================================================
# Domain Enums
# ============================================================================

class AirStatus(str, Enum):
    OPTIMAL = "optimal"
    MODERATE = "moderate"
    BAD = "bad"


class GroundStatus(str, Enum):
    DRY = "dry"
    OPTIMAL = "optimal"


# ============================================================================
# Plant Domain Models
# ============================================================================

class AirInfo(BaseModel):
    temperature: str
    humidity: str
    status: AirStatus


class GroundInfo(BaseModel):
    humidity: str
    status: GroundStatus


class PlantInfo(BaseModel):
    air: AirInfo
    ground: GroundInfo


# ============================================================================
# Request/Response Models
# ============================================================================

class HealthData(BaseModel):
    service: str
    version: str
    mode: str


class WateringRequest(BaseModel):
    duration_seconds: int = 5  # Default 5 seconds valve open


class WateringData(BaseModel):
    triggered: bool
    duration_seconds: int
    message: str
