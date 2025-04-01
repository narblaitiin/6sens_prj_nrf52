# Using a Systemd Servcie

## 1. Create a service file:

sudo nano /etc/systemd/system/weatherstation.service

## 2. Add the following:

[Unit]

Description=Weather Station Script
After=multi-user.target

[Service]

ExecStart=/usr/bin/python3 /path/to/your_script.py
WorkingDirectory=/home/pi
StandardOutput=inherit
StandardError=inherit
Restart=always
User=pi

[Install]

WantedBy=multi-user.target

## 3. Enable and start the service:

sudo systemctl enable weatherstation.service
sudo systemctl start weatherstation.service

## 4. Check status:

sudo systemctl status weatherstation.service

## 5. Reboot to verify it starts automatically.