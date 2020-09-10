import time

from pyfiglet import Figlet
from beacontools import BeaconScanner, IBeaconFilter, IBeaconAdvertisement, parse_packet
from .models import TiltStatus
from .abstractions import CloudProviderBase
from .providers import PrometheusCloudProvider, WebhookCloudProvider
from .configuration import PitchConfig

#############################################
# Statics
#############################################
color_map = {
        "a495bb20-c5b1-4b44-b512-1370f02d74de": "green",
        "a495bb30-c5b1-4b44-b512-1370f02d74de": "black",
        "a495bb10-c5b1-4b44-b512-1370f02d74de": "red",
        "a495bb60-c5b1-4b44-b512-1370f02d74de": "blue",
        "a495bb50-c5b1-4b44-b512-1370f02d74de": "orange",
        "a495bb70-c5b1-4b44-b512-1370f02d74de": "pink",
        "a495bb40-c5b1-4b44-b512-1370f02d74de": "purple"
    }

all_providers = [
        PrometheusCloudProvider()
    ]

enabled_providers = list()

#############################################
#############################################

def pitch_main():
    start_message()
    # Load config
    config = PitchConfig.load()
    # add any webhooks defined in config
    add_webhook_providers(config)
    # Start cloud providers
    print("Starting...")
    for provider in all_providers:
        if provider.enabled():
            enabled_providers.append(provider)
            provider_start_message = provider.start()
            if not provider_start_message:
                provider_start_message = ''
            print("...started: {} {}".format(provider, provider_start_message))

    scanner = BeaconScanner(beacon_callback)
    scanner.start()
    print("...started: Tilt scanner")

    print("Ready!  Listening for beacons")

def beacon_callback(bt_addr, rssi, packet, additional_info):
    uuid = packet.uuid
    color = color_map.get(uuid)
    if color:
        # iBeacon packets have major/minor attributes with data
        # major = degrees in F (int)
        # minor = gravity (int) - needs to be converted to float (e.g. 1035 -> 1.035)
        tilt_status = TiltStatus(color, packet.major, get_decimal_gravity(packet.minor))
        # Update in enabled providers
        for provider in enabled_providers:
            provider.update(tilt_status)
        # Log it to console/stdout
        print(tilt_status.json())

def get_decimal_gravity(gravity):
    # gravity will be an int like 1035
    # turn into decimal, like 1.035
    return gravity * .001

def add_webhook_providers(config: PitchConfig):
    # Multiple webhooks can be fired, so create them dynamically and add to
    # all providers static list
    for url in config.webhook_urls:
        all_providers.append(WebhookCloudProvider(url))

def start_message():
    f = Figlet(font='slant')
    print(f.renderText('Pitch'))