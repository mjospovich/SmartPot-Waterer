#!/usr/bin/env python3
"""
HC-05 Bluetooth Connection Test Script
Run: python -m api.test_bluetooth
"""

import sys
import time
import serial
import serial.tools.list_ports


def list_serial_ports():
    """List all available serial ports."""
    ports = serial.tools.list_ports.comports()
    print("\n📡 Available serial ports:")
    print("-" * 40)
    
    if not ports:
        print("  No serial ports found!")
        return []
    
    for port in ports:
        print(f"  {port.device}")
        print(f"    Description: {port.description}")
        print(f"    HWID: {port.hwid}")
        print()
    
    return [p.device for p in ports]


def test_connection(port: str, baud_rate: int = 9600):
    """Test connection to HC-05 module."""
    print(f"\n🔌 Connecting to {port} at {baud_rate} baud...")
    
    try:
        connection = serial.Serial(
            port=port,
            baudrate=baud_rate,
            timeout=2.0
        )
        print("✅ Connection established!")
        return connection
    except serial.SerialException as e:
        print(f"❌ Connection failed: {e}")
        return None


def send_command(connection: serial.Serial, command: str) -> str:
    """Send a command and read response."""
    try:
        print(f"\n📤 Sending: {command}")
        connection.write(f"{command}\n".encode())
        
        time.sleep(0.5)  # Wait for Arduino to process
        
        response = ""
        while connection.in_waiting:
            response += connection.readline().decode().strip() + "\n"
        
        if response:
            print(f"📥 Response: {response.strip()}")
        else:
            print("📥 No response received")
        
        return response.strip()
    except serial.SerialException as e:
        print(f"❌ Error: {e}")
        return ""


def interactive_mode(connection: serial.Serial):
    """Interactive command mode."""
    print("\n" + "=" * 40)
    print("🎮 Interactive Mode")
    print("=" * 40)
    print("Commands:")
    print("  READ     - Read sensor data")
    print("  WATER:5  - Water for 5 seconds")
    print("  PING     - Test connection")
    print("  quit     - Exit")
    print("-" * 40)
    
    while True:
        try:
            cmd = input("\n> ").strip()
            if cmd.lower() in ("quit", "exit", "q"):
                break
            if cmd:
                send_command(connection, cmd)
        except (KeyboardInterrupt, EOFError):
            print()  # Newline after ^C
            break


def main():
    print("=" * 40)
    print("🌱 SmartPot HC-05 Bluetooth Tester")
    print("=" * 40)
    
    # List available ports
    ports = list_serial_ports()
    
    # Check for HC-05 in common locations
    hc05_candidates = [p for p in ports if "HC-05" in p or "Bluetooth" in p.lower()]
    
    # Get port from user or use default
    if len(sys.argv) > 1:
        port = sys.argv[1]
    elif hc05_candidates:
        port = hc05_candidates[0]
        print(f"🎯 Auto-detected HC-05: {port}")
    else:
        port = input("\nEnter port (e.g., /dev/tty.HC-05): ").strip()
    
    if not port:
        print("❌ No port specified. Exiting.")
        return
    
    # Connect
    connection = test_connection(port)
    if not connection:
        return
    
    try:
        # Quick ping test
        print("\n🏓 Sending PING...")
        send_command(connection, "PING")
        
        # Enter interactive mode
        interactive_mode(connection)
    except KeyboardInterrupt:
        print()
    finally:
        print("👋 Closing connection...")
        try:
            connection.close()
        except (OSError, serial.SerialException):
            pass  # Already closed or interrupted
        print("🔌 Done.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🔌 Interrupted.")
        sys.exit(0)
