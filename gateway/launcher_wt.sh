#!/usr/bin/sh
# satsress project
# weather sation code for the LoRaWAN gateway with MQTT
# version 1.0 - 25/03/2025

## Launch Python Script on Startup
# make it executable: chmod 755 launcher_wt.sh
# add to logs directory: mkdir logs
# add to your crontab: sudo crontab -e then enter the line: @reboot sh /home/pi/bbt/launcher.sh >/home/pi/logs/cronlog 2>&1
# reboot
# test: cd logs then cat cronlog



cd /
cd /home/admin/weather-station/
python3 weather-station-mqtt.py
cd /



