from beacontools import BeaconScanner, IBeaconFilter, IBeaconAdvertisement, parse_packet
from prometheus_client import start_http_server, Counter, Gauge

from . import beacon_callback

if __name__ == '__main__':
    # scan for all iBeacon advertisements from beacons with certain properties:
    # - uuid
    # - major
    # - minor
    # at least one must be specified.
    print("Starting...")
    port=8000
    start_http_server(port)
    print("  ...started metrics server port (127.0.0.1:{}/metrics)".format(port))

    scanner = BeaconScanner(beacon_callback)
    scanner.start()
    print("  ...started beacon scanner")

    print("Ready!  Listening for beacons")

    