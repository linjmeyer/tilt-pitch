import time
import json

from beacontools import BeaconScanner, IBeaconFilter, IBeaconAdvertisement, parse_packet
from prometheus_client import start_http_server, Counter, Gauge

class TiltStatus:

    def __init__(self, color, temp_f, gravity):
        self.color = color
        self.temp_f = temp_f
        self.temp_c = get_celcius(temp_f)
        self.gravity = gravity

    def json(self):
        return json.dumps(self.__dict__)

# statics
color_map = {
        "a495bb20-c5b1-4b44-b512-1370f02d74de": "green",
        "a495bb30-c5b1-4b44-b512-1370f02d74de": "black",
        "a495bb10-c5b1-4b44-b512-1370f02d74de": "red",
        "a495bb60-c5b1-4b44-b512-1370f02d74de": "blue",
        "a495bb50-c5b1-4b44-b512-1370f02d74de": "orange",
        "a495bb70-c5b1-4b44-b512-1370f02d74de": "pink",
        "a495bb40-c5b1-4b44-b512-1370f02d74de": "purple"
    }

counter_beacons_received = Counter('pitch_beacons_received', 'Number of beacons received', ['color'])
gauge_temperature_fahrenheit = Gauge('pitch_temperature_fahrenheit', 'Temperature in fahrenheit', ['color'])
gauge_temperature_celcius = Gauge('pitch_temperature_celcius', 'Temperature in celcius', ['color'])
gauge_gravity = Gauge('pitch_gravity', 'Gravity of the beer', ['color'])
#########

def callback(bt_addr, rssi, packet, additional_info):
    uuid = packet.uuid
    color = color_map.get(uuid)
    if color:
        # iBeacon packets have major/minor attributes with data
        # major = degrees in F (int)
        # minor = gravity (int) - needs to be converted to float (e.g. 1035 -> 1.035)
        tilt_status = TiltStatus(color, packet.major, get_decimal_gravity(packet.minor))
        tilt_metrics(tilt_status)
        tilt_hooks(tilt_status)

def tilt_metrics(tilt_status: TiltStatus):
    counter_beacons_received.labels(color=tilt_status.color).inc()
    gauge_temperature_fahrenheit.labels(color=tilt_status.color).set(tilt_status.temp_f)
    gauge_temperature_celcius.labels(color=tilt_status.color).set(tilt_status.temp_c)
    gauge_gravity.labels(color=tilt_status.color).set(tilt_status.gravity)

def tilt_hooks(tilt_status: TiltStatus):
    print("-------------------------------------------")
    print("Broadcoast for device:   {}".format(tilt_status.color))
    print("Temperature:             {}f ({}c)".format(tilt_status.temp_f, tilt_status.temp_c))
    print("Gravity:                 {}".format(tilt_status.gravity))
    print("Json:                    {}".format(tilt_status.json()))

def get_decimal_gravity(gravity):
    # gravity will be an int like 1035
    # turn into decimal, like 1.035
    return gravity * .001

def get_celcius(temp_f):
    return round((temp_f - 32) * 5.0/9.0)


# scan for all iBeacon advertisements from beacons with certain properties:
# - uuid
# - major
# - minor
# at least one must be specified.
print("Starting...")
scanner = BeaconScanner(callback)
scanner.start()
print("  ...started beacon scanner")

port=8000
start_http_server(port)
print("  ...started metrics server port (127.0.0.1:{}/metrics)".format(port))