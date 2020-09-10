from beacontools import BeaconScanner, IBeaconFilter, IBeaconAdvertisement, parse_packet

from .providers import PrometheusCloudProvider
from . import beacon_callback

if __name__ == '__main__':
    # Start all cloud providers
    all_providers = [
        PrometheusCloudProvider()
    ]
    print("Starting cloud providers...")
    for provider in all_providers:
        if provider.enabled():
            provider.start()
            print("...started: {}".format(provider))

    print("Starting Tilt scanner...")
    scanner = BeaconScanner(beacon_callback)
    scanner.start()
    print("...started Tilt scanner")

    print("Ready!  Listening for beacons")

    