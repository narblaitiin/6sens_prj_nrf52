#! /usr/bin/env python3
# satsress project
# weather sation code for the LoRaWAN gateway with MQTT
# version 1.0 - 25/03/2025
# version 1.1 - 01/04/2025 (add date and time in payload)

import RPi.GPIO as GPIO
import json
import threading

from time import sleep
from datetime import datetime

import board
import busio
from adafruit_bme280 import basic as adafruit_bme280
import paho.mqtt.client as mqtt

from w1thermsensor import W1ThermSensor

import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Initialize sensors
i2c = busio.I2C(board.SCL, board.SDA)
bme = adafruit_bme280.Adafruit_BME280_I2C(i2c)
ds18b20 = W1ThermSensor()
ads = ADS.ADS1015(i2c)
ads.gain = 1

# GPIO setup
GPIO.setmode(GPIO.BCM)
WIND_PIN = 23  # Wind speed sensor GPIO pin
RAIN_PIN = 17  # Rain sensor GPIO pin
GPIO.setup(WIND_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(RAIN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# MQTT setup
BROKER_ADDRESS = "sastress.citi.insa-lyon.fr"  # Replace with your MQTT broker address
PORT = 8080
TOPIC = "v3/sastress-stm32-app@wifi/gateway-status"  # Replace with your desired topic

client = mqtt.Client()
client.username_pw_set("sastress-gateway", "URTssVNrfXB1mp7TO")
client.connect(BROKER_ADDRESS, PORT, 120)

# Global variables
wind_count = 0
rain_cum = 0.0
BUCKET_SIZE = 0.2794  # Adjust based on rain gauge calibration
interval = 60  # Interval in seconds for data collection
speed = []
wind_deg = []

chan = AnalogIn(ads, ADS.P0)
val = chan.value

# Wind direction logic
def get_wind_direction(val):
    wind_deg = 0
    if 20000 <= val <= 20500:
        wind_deg = 0
    elif 10000 <= val <= 10500:
        wind_deg = 22.5
    elif 11500 <= val <= 12000:
        wind_deg = 45
    elif 2000 <= val <= 2250:
        wind_deg = 67.5
    elif 2300 <= val <= 2500:
        wind_deg = 90
    elif 1500 <= val <= 1950:
        wind_deg = 112.5
    elif 4500 <= val <= 4900:
        wind_deg = 135
    elif 3000 <= val <= 3500:
        wind_deg = 157.5
    elif 7000 <= val <= 7500:
        wind_deg = 180
    elif 6000 <= val <= 6500:
        wind_deg = 202.5
    elif 16000 <= val <= 16500:
        wind_deg = 225
    elif 15000 <= val <= 15500:
        wind_deg = 247.5
    elif 24000 <= val <= 24500:
        wind_deg = 270
    elif 2100 <= val <= 21500:
        wind_deg = 292.5
    elif 22500 <= val <= 23000:
        wind_deg = 315
    elif 17500 <= val <= 18500:
        wind_deg = 337.5
    return wind_deg

# Increment wind count
def wind_event(channel):
    global wind_count
    wind_count += 1

# Increment rain bucket count
def rain_event(channel):
    global rain_cum
    rain_cum += BUCKET_SIZE

# Calculate wind speed
def wind_speed(interval):
    global wind_count
    speed = wind_count * 2.4 / interval  # Adjust multiplier based on calibration
    wind_count = 0
    return speed

# Temperature and humidity
def temperature():
    return ds18b20.get_temperature()

def humidity():
    return bme.humidity

# Collect and send data
def collect_data():
    global speed, wind_deg, rain_cum
    i = 0
    while True:
        sleep(interval)
        speed.append(wind_speed(interval))
        wind_deg.append(get_wind_direction(0))  # Replace `0` with actual sensor value
        i += 1
        if i == 15:  # Send data every 15 intervals
            dt = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            temper = temperature()
            hum = humidity()
            speed_avg = sum(speed) / len(speed)
            dir_avg = sum(wind_deg) / len(wind_deg) if wind_deg else 0
            payload = json.dumps({
                "time": dt,
                "rain": rain_cum,
                "temperature": temper,
                "humidity": hum,
                "wind_speed": speed_avg,
                "wind_dir": dir_avg
            })
            print(payload)
            client.publish(TOPIC, payload)
            i = 0
            speed.clear()
            wind_deg.clear()

# Set up GPIO event detection
GPIO.add_event_detect(WIND_PIN, GPIO.FALLING, callback=wind_event, bouncetime=300)
GPIO.add_event_detect(RAIN_PIN, GPIO.FALLING, callback=rain_event, bouncetime=300)

# Start data collection
collect_data()