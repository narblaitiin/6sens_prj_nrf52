#! /usr/bin/env python3
# satsress project
# weather sation code for the LoRaWAN gateway
# version 1.0 - 25/03/2025

import time
from time import sleep
from time import strftime
from w1thermsensor import W1ThermSensor

import board
import busio
from adafruit_bme280 import basic as adafruit_bme280
i2c = busio.I2C(board.SCL, board.SDA)

import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

import RPi.GPIO as GPIO
import requests

import random
import paho.mqtt.client as mqtt
import json

broker = 'sastress.citi.insa-lyon.fr'
# broker = 'sastress.project.citi-lab.fr'

# port = 1883
port = 8080

topic = "sastress/gateway-status"
client_id = f'python-mqtt-{random.randint(0, 100)}'

def on_connect(client,userdata,flags,rc):
    if rc==0:
        print("Connected OK")
    else:
        print("Bad connetion Retruned Code=",rc)

mqtt_c=mqtt.Client(client_id)
mqtt_c.on_connect=on_connect
mqtt_c.username_pw_set("sastress-front",password="")
mqtt_c.connect(broker, port)
mqtt_c.loop_start()

bme = adafruit_bme280.Adafruit_BME280_I2C(i2c)
ads = ADS.ADS1015(i2c)
ads.gain = 1

ds18b20 = W1ThermSensor()

interval = 300  # how long we want to wait between loops (seconds)
windTick = 0    # used to count the number of times the wind speed input is triggered
rainTick = 0    # used to count the number of times the rain input is triggered

# set GPIO pins to use BCM pin numbers
GPIO.setmode(GPIO.BCM)

# set digital pin 17 to an input and enable the pullup
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# wet digital pin 23 to an input and enable the pullup
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# event to detect wind (4 ticks per revolution)
GPIO.add_event_detect(17, GPIO.BOTH)
def windtrig(self):
    global windTick
    windTick += 1

GPIO.add_event_callback(17, windtrig)

# event to detect rainfall tick
GPIO.add_event_detect(23, GPIO.FALLING)
def raintrig(self):
    global rainTick
    rainTick += 1

GPIO.add_event_callback(23, raintrig)

while True:

    time.sleep(interval)

    # grab the current date & time
    timestamp = time.strftime("%Y-%m-%d_%H:%M:%S")

    # pull Temperature from DS18B20
    temperature = ds18b20.get_temperature()

    # pull pressure from BME280 Sensor & convert to kPa
    pressure_pa = bme.pressure
    pressure = pressure_pa / 10

    # pull humidity from BME280
    humidity = bme.humidity

    # calculate wind direction based on ADC reading
    chan = AnalogIn(ads, ADS.P0)
    val = chan.value
    windDir = "Not Connected"
    windDeg = 999

    if 20000 <= val <= 20500:
        windDir = "N"
        windDeg = 0

    if 10000 <= val <= 10500:
        windDir = "NNE"
        windDeg = 22.5

    if 11500 <= val <= 12000:
        windDir = "NE"
        windDeg = 45

    if 2000 <= val <= 2250:
        windDir = "ENE"
        windDeg = 67.5

    if 2300 <= val <= 2500:
        windDir = "E"
        windDeg = 90

    if 1500 <= val <= 1950:
        windDir = "ESE"
        windDeg = 112.5

    if 4500 <= val <= 4900:
        windDir = "SE"
        windDeg = 135

    if 3000 <= val <= 3500:
        windDir = "SSE"
        windDeg = 157.5

    if 7000 <= val <= 7500:
        windDir = "S"
        windDeg = 180

    if 6000 <= val <= 6500:
        windDir = "SSW"
        windDeg = 202.5

    if 16000 <= val <= 16500:
        windDir = "SW"
        windDeg = 225

    if 15000 <= val <= 15500:
        windDir = "WSW"
        windDeg = 247.5

    if 24000 <= val <= 24500:
        windDir = "W"
        windDeg = 270

    if 21000 <= val <= 21500:
        windDir = "WNW"
        windDeg = 292.5

    if 22500 <= val <= 23000:
        windDir = "NW"
        windDeg = 315

    if 17500 <= val <= 18500:
        windDir = "NNW"
        windDeg = 337.5

    # calculate average windspeed over the last 15 seconds
    windSpeed = (windTick * 1.2) / 15
    windTick = 0

    # calculate accumulated rainfall over the last 15 seconds
    rainFall = rainTick * 0.2794
    rainTick = 0

    # configure parameters to send
    payload = json.dumps({'Timestamp':timestamp,'Temperature':temperature,'Vitesse':windSpeed,'Direction': windDeg,'Pluviometrie':rainFall})
    mqtt_c.publish(topic, payload)
