import time

from beacontools import BeaconScanner, IBeaconFilter, IBeaconAdvertisement, parse_packet

color_map = {
        "a495bb20-c5b1-4b44-b512-1370f02d74de": "Green",
        "a495bb30-c5b1-4b44-b512-1370f02d74de": "Black",
        "a495bb10-c5b1-4b44-b512-1370f02d74de": "Red",
        "a495bb60-c5b1-4b44-b512-1370f02d74de": "Blue",
        "a495bb50-c5b1-4b44-b512-1370f02d74de": "Orange",
        "a495bb70-c5b1-4b44-b512-1370f02d74de": "Pink",
        "a495bb40-c5b1-4b44-b512-1370f02d74de": "Purple"
    }

def callback(bt_addr, rssi, packet, additional_info):
    uuid = packet.uuid
    color = color_map.get(uuid)
    if color:
        # iBeacon packets have major/minor attributes with data
        # major = degrees in F (int)
        # minor = gravity (int) - needs to be converted to float (e.g. 1035 -> 1.035)
        tilt_hooks(color, packet.major, get_decimal_gravity(packet.minor))
    
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
scanner = BeaconScanner(callback)
scanner.start()