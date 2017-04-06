from __future__ import print_function

import datetime
import sys
import time

from bluepy.btle import BTLEException
from bluepy.sensortag import SensorTag
from Adafruit_IO import *


# configurations to be set accordingly
SENSORTAG_ADDRESS = "24:71:89:BD:10:01"
FREQUENCY_SECONDS = 60.0
aio = Client('7694b7ba068142a3a0c2afaadffc9d53')

def enable_sensors(tag):
    """Enable sensors so that readings can be made."""
    tag.IRtemperature.enable()
    tag.accelerometer.enable()
    tag.humidity.enable()
    tag.magnetometer.enable()
    tag.barometer.enable()
    tag.gyroscope.enable()
    tag.keypress.enable()
    tag.lightmeter.enable()
    # tag.battery.enable()

    # Some sensors (e.g., temperature, accelerometer) need some time for initialization.
    # Not waiting here after enabling a sensor, the first read value might be empty or incorrect.
    time.sleep(1.0)

def disable_sensors(tag):
    """Disable sensors to improve battery life."""
    tag.IRtemperature.disable()
    tag.accelerometer.disable()
    tag.humidity.disable()
    tag.magnetometer.disable()
    tag.barometer.disable()
    tag.gyroscope.disable()
    tag.keypress.disable()
    tag.lightmeter.disable()
    # tag.battery.disable()


def get_readings(tag):
    """Get sensor readings and collate them in a dictionary."""
    try:
        enable_sensors(tag)
        readings = {}
        # IR sensor
        readings["ir_temp"], readings["ir"] = tag.IRtemperature.read()
        # humidity sensor
        readings["humidity_temp"], readings["humidity"] = tag.humidity.read()
        # barometer
        readings["baro_temp"], readings["pressure"] = tag.barometer.read()
        # luxmeter
        readings["light"] = tag.lightmeter.read()
        # battery
        # readings["battery"] = tag.battery.read()
        disable_sensors(tag)

        # round to 2 decimal places for all readings
        readings = {key: round(value, 2) for key, value in readings.items()}
        return readings

    except BTLEException as e:
        print("Unable to take sensor readings.")
        print(e)
        return {}


def reconnect(tag):
    try:
        tag.connect(tag.deviceAddr, tag.addrType)

    except Exception as e:
        print("Unable to reconnect to SensorTag.")
        raise e


def main():
    print('Connecting to {}'.format(SENSORTAG_ADDRESS))
    tag = SensorTag(SENSORTAG_ADDRESS)

    print('Logging sensor measurements every {0} seconds.'.format(FREQUENCY_SECONDS))
    print('Press Ctrl-C to quit.')
    while True:
        # get sensor readings
        readings = get_readings(tag)
        if not readings:
            print("SensorTag disconnected. Reconnecting.")
            reconnect(tag)
            continue

        # print readings
        print("Time:\t{}".format(datetime.datetime.now()))
        print("IR reading:\t\t{}, temperature:\t{}".format(readings["ir"], readings["ir_temp"]))
        aio.send('WeatherTempIr', format(readings["ir"], readings["ir_temp"]))
        print("Humidity reading:\t{}, temperature:\t{}".format(readings["humidity"], readings["humidity_temp"]))
        print("Barometer reading:\t{}, temperature:\t{}".format(readings["pressure"], readings["baro_temp"]))
        print("Luxmeter reading:\t{}".format(readings["light"]))

        print()
        time.sleep(FREQUENCY_SECONDS)


if __name__ == "__main__":
    main()
