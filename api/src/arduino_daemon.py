#!/usr/bin/env python3
"""
SmartPot Arduino Daemon

Background service that:
1. Maintains serial connection to Arduino via /dev/rfcomm0
2. Reads sensor data and writes to sensor_data.json
3. Watches for commands in command.txt and sends to Arduino

Run as systemd service on Raspberry Pi.
"""

import os
import re
import json
import time
import serial
import logging
from pathlib import Path
from datetime import datetime

# ============================================================================
# Configuration
# ============================================================================

SERIAL_PORT = os.getenv("SERIAL_PORT", "/dev/rfcomm0")
BAUD_RATE = int(os.getenv("BAUD_RATE", "9600"))
SERIAL_TIMEOUT = 2

# Paths - relative to this script's location
SCRIPT_DIR = Path(__file__).parent.parent  # api/
DATA_DIR = SCRIPT_DIR / "data"
SENSOR_FILE = DATA_DIR / "sensor_data.json"
COMMAND_FILE = DATA_DIR / "command.txt"

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("arduino_daemon")


# ============================================================================
# Sensor Data Parser
# ============================================================================

def parse_sensor_line(line: str, current_data: dict) -> dict:
    """
    Parse a line from Arduino output and update sensor data.
    
    Arduino sends:
        --------------------
        Temp: 21.20 C
        Humi: 45.00 %
        Soil: 73 %
    """
    line = line.strip()
    
    # Temperature
    match = re.match(r"Temp:\s*([\d.]+)\s*C", line)
    if match:
        current_data["temperature"] = float(match.group(1))
        return current_data
    
    # Air Humidity
    match = re.match(r"Humi:\s*([\d.]+)\s*%", line)
    if match:
        current_data["air_humidity"] = float(match.group(1))
        return current_data
    
    # Soil Humidity
    match = re.match(r"Soil:\s*(\d+)\s*%", line)
    if match:
        current_data["soil_humidity"] = int(match.group(1))
        return current_data
    
    # Servo status
    if line.startswith("Servo:"):
        current_data["last_servo_action"] = line
        current_data["last_servo_time"] = datetime.now().isoformat()
        return current_data
    
    return current_data


def determine_statuses(data: dict) -> dict:
    """Add status fields based on sensor values."""
    temp = data.get("temperature", 0)
    air_hum = data.get("air_humidity", 0)
    soil_hum = data.get("soil_humidity", 0)
    
    # Air status
    if 18 <= temp <= 28 and 40 <= air_hum <= 70:
        data["air_status"] = "optimal"
    elif 15 <= temp <= 32 and 30 <= air_hum <= 80:
        data["air_status"] = "moderate"
    else:
        data["air_status"] = "bad"
    
    # Ground status
    data["ground_status"] = "optimal" if soil_hum >= 40 else "dry"
    
    return data


def save_sensor_data(data: dict):
    """Write sensor data to JSON file."""
    data["last_updated"] = datetime.now().isoformat()
    
    # Ensure data directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(SENSOR_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to write sensor data: {e}")


# ============================================================================
# Command Handler
# ============================================================================

def check_and_send_command(ser: serial.Serial) -> bool:
    """
    Check for command file and send command to Arduino.
    Returns True if a command was sent.
    """
    if not COMMAND_FILE.exists():
        return False
    
    try:
        command = COMMAND_FILE.read_text().strip()
        if command:
            logger.info(f"Sending command: {command}")
            ser.write(f"{command}\n".encode())
            ser.flush()
        
        # Remove command file after processing
        COMMAND_FILE.unlink()
        return True
    except Exception as e:
        logger.error(f"Failed to process command: {e}")
        return False


# ============================================================================
# Main Loop
# ============================================================================

def run_daemon():
    """Main daemon loop."""
    logger.info("=" * 50)
    logger.info("SmartPot Arduino Daemon Starting")
    logger.info(f"Serial Port: {SERIAL_PORT}")
    logger.info(f"Data File: {SENSOR_FILE}")
    logger.info("=" * 50)
    
    # Ensure data directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    sensor_data = {
        "temperature": None,
        "air_humidity": None,
        "soil_humidity": None,
        "air_status": "unknown",
        "ground_status": "unknown",
        "last_updated": None,
        "daemon_status": "starting"
    }
    
    while True:
        try:
            logger.info(f"Connecting to {SERIAL_PORT}...")
            
            with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=SERIAL_TIMEOUT) as ser:
                logger.info("Connected to Arduino")
                sensor_data["daemon_status"] = "connected"
                save_sensor_data(sensor_data)
                
                while True:
                    # Check for commands first
                    check_and_send_command(ser)
                    
                    # Read available data
                    if ser.in_waiting > 0:
                        try:
                            line = ser.readline().decode("utf-8", errors="ignore")
                            if line.strip():
                                logger.debug(f"RX: {line.strip()}")
                                sensor_data = parse_sensor_line(line, sensor_data)
                                sensor_data = determine_statuses(sensor_data)
                                save_sensor_data(sensor_data)
                        except Exception as e:
                            logger.warning(f"Read error: {e}")
                    
                    # Small sleep to prevent CPU spinning
                    time.sleep(0.1)
                    
        except serial.SerialException as e:
            logger.error(f"Serial error: {e}")
            sensor_data["daemon_status"] = "disconnected"
            save_sensor_data(sensor_data)
            logger.info("Retrying in 5 seconds...")
            time.sleep(5)
            
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            sensor_data["daemon_status"] = "stopped"
            save_sensor_data(sensor_data)
            break
            
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            sensor_data["daemon_status"] = "error"
            save_sensor_data(sensor_data)
            time.sleep(5)


if __name__ == "__main__":
    run_daemon()
