# SmartPot API - Mock Frontend

Simple reference for API routes and responses.

## Setup

1. Start the API: `./run.sh` (runs on port 8001)
2. Open `index.html` in browser

## Routes

### GET /health
```json
{
  "status": "success",
  "data": {
    "service": "SmartPot API",
    "version": "1.0.0",
    "mode": "mock"
  },
  "error": null
}
```

### GET /plant
```json
{
  "status": "success",
  "data": {
    "plant_info": {
      "air": {
        "temperature": "23.5C",
        "humidity": "65.2%",
        "status": "optimal"
      },
      "ground": {
        "humidity": "45.3%",
        "status": "optimal"
      }
    }
  },
  "error": null
}
```

### POST /water
Request:
```json
{ "duration_seconds": 5 }
```

Response:
```json
{
  "status": "success",
  "data": {
    "triggered": true,
    "duration_seconds": 5,
    "message": "Watering simulated for 5 seconds"
  },
  "error": null
}
```

## Error Response Format
```json
{
  "status": "error",
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "Description",
    "details": "Optional details"
  }
}
```
