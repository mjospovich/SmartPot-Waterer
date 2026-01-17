import os
import serial
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class ArduinoController:
    """Handles Bluetooth serial communication with the Arduino."""
    
    def __init__(self):
        # Bluetooth serial port (e.g., /dev/tty.HC-05 on macOS)
        self.port: str = os.getenv("ARDUINO_BT_PORT", "/dev/tty.HC-05")
        self.baud_rate: int = int(os.getenv("ARDUINO_BAUD_RATE", "9600"))
        self.timeout: float = float(os.getenv("ARDUINO_TIMEOUT", "2.0"))
        self._connection: Optional[serial.Serial] = None
    
    def connect(self) -> bool:
        """Establish Bluetooth connection to Arduino."""
        try:
            self._connection = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                timeout=self.timeout
            )
            logger.info(f"Connected to Arduino via Bluetooth on {self.port}")
            return True
        except serial.SerialException as e:
            logger.error(f"Failed to connect to Arduino via Bluetooth: {e}")
            return False
    
    def disconnect(self) -> None:
        """Close the Bluetooth connection."""
        if self._connection and self._connection.is_open:
            self._connection.close()
            logger.info("Disconnected from Arduino")
    
    def send_command(self, command: str) -> bool:
        """Send a command to the Arduino over Bluetooth."""
        if not self._connection or not self._connection.is_open:
            if not self.connect():
                return False
        
        try:
            self._connection.write(f"{command}\n".encode())
            logger.info(f"Sent command to Arduino: {command}")
            return True
        except serial.SerialException as e:
            logger.error(f"Failed to send command: {e}")
            return False
    
    def trigger_watering(self, duration_seconds: int = 5) -> bool:
        """
        Send command to open the water valve via servo motor.
        Arduino will rotate servo to open valve, wait, then close.
        """
        return self.send_command(f"WATER:{duration_seconds}")
    
    def read_sensor_data(self) -> Optional[dict]:
        """Read sensor data from Arduino over Bluetooth."""
        if not self._connection or not self._connection.is_open:
            if not self.connect():
                return None
        
        try:
            self._connection.write(b"READ\n")
            response = self._connection.readline().decode().strip()
            
            if response:
                # Expected format: "TEMP:23.5,AIR_HUM:65.2,GROUND_HUM:69.5"
                data = {}
                for pair in response.split(","):
                    if ":" in pair:
                        key, value = pair.split(":", 1)
                        data[key.strip()] = value.strip()
                return data
            return None
        except serial.SerialException as e:
            logger.error(f"Failed to read sensor data: {e}")
            return None


# Singleton instance
arduino = ArduinoController()
