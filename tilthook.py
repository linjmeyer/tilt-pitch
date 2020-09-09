import time

from beacontools import BeaconScanner, IBeaconFilter, IBeaconAdvertisement, parse_packet
from prometheus_client import start_http_server, Counter, Gauge

# statics
color_map = {
        "a495bb20-c5b1-4b44-b512-1370f02d74de": "Green",
        "a495bb30-c5b1-4b44-b512-1370f02d74de": "Black",
        "a495bb10-c5b1-4b44-b512-1370f02d74de": "Red",
        "a495bb60-c5b1-4b44-b512-1370f02d74de": "Blue",
        "a495bb50-c5b1-4b44-b512-1370f02d74de": "Orange",
        "a495bb70-c5b1-4b44-b512-1370f02d74de": "Pink",
        "a495bb40-c5b1-4b44-b512-1370f02d74de": "Purple"
    }

counter_beacons_received = Counter('beacons_received', 'Number of beacons received', ['color'])
gauge_temperature_fahrenheit = Gauge('emperature_fahrenheit', 'Temperature in fahrenheit', ['color'])
gauge_gravity = Gauge('gravity', 'Gravity of the beer', ['color'])
#########

def callback(bt_addr, rssi, packet, additional_info):
    uuid = packet.uuid
    color = color_map.get(uuid)
    if color:
        # iBeacon packets have major/minor attributes with data
        # major = degrees in F (int)
        # minor = gravity (int) - needs to be converted to float (e.g. 1035 -> 1.035)
        gravity = get_decimal_gravity(packet.minor)
        degrees_f = packet.major
        tilt_metrics(color, degrees_f, gravity)
        tilt_hooks(color, degrees_f, gravity)

def tilt_metrics(color, temp_f, gravity):
    counter_beacons_received.labels(color=color).inc()
    gauge_temperature_fahrenheit.labels(color=color).set(temp_f)
    gauge_gravity.labels(color=color).set(gravity)

def tilt_hooks(color, temp_f, gravity):
    print("-------------------------------------------")
    print("Broadcoast for device: {}".format(color))
    print("Temperature: {}F".format(temp_f))
    print("Gravity: {}".format(gravity))

def get_decimal_gravity(gravity):
    # gravity will be an int like 1035
    # turn into decimal, like 1.035
    return gravity * .001
    

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