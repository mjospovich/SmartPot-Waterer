# SmartPot Systemd Services

Service files for running SmartPot on Raspberry Pi.

## Services

| Service | Purpose |
|---------|---------|
| `rfcomm-hc05.service` | Binds Bluetooth HC-05 to /dev/rfcomm0 |
| `smartpot-daemon.service` | Reads Arduino data, writes to JSON |
| `smartpot-api.service` | FastAPI server |

## Installation

```bash
# Copy service files
sudo cp systemd/*.service /etc/systemd/system/

# Create rfcomm service (if not already done)
sudo nano /etc/systemd/system/rfcomm-hc05.service
```

Add to rfcomm-hc05.service:
```ini
[Unit]
Description=RFCOMM bind for HC-05
After=bluetooth.target

[Service]
Type=oneshot
ExecStart=/usr/bin/rfcomm bind 0 [MAC_ADDRESS] 1
ExecStop=/usr/bin/rfcomm release 0
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

Then enable all services:
```bash
sudo systemctl daemon-reload

# Enable services (start on boot)
sudo systemctl enable rfcomm-hc05.service
sudo systemctl enable smartpot-daemon.service
sudo systemctl enable smartpot-api.service

# Start services now
sudo systemctl start rfcomm-hc05.service
sudo systemctl start smartpot-daemon.service
sudo systemctl start smartpot-api.service
```

## Checking Status

```bash
# Check all services
sudo systemctl status rfcomm-hc05
sudo systemctl status smartpot-daemon
sudo systemctl status smartpot-api

# View logs
journalctl -u smartpot-daemon -f
journalctl -u smartpot-api -f
```

## Data Files

The daemon writes to:
- `api/data/sensor_data.json` - Current sensor readings
- `api/data/command.txt` - Command queue (auto-deleted after processing)
