import argparse
import threading
import time
from pyfiglet import Figlet
from beacontools import BeaconScanner
from .models import TiltStatus
from .providers import PrometheusCloudProvider, WebhookCloudProvider, FileCloudProvider, InfluxDbCloudProvider
from .configuration import PitchConfig

#############################################
# Statics
#############################################
uuid_to_colors = {
        "a495bb20-c5b1-4b44-b512-1370f02d74de": "green",
        "a495bb30-c5b1-4b44-b512-1370f02d74de": "black",
        "a495bb10-c5b1-4b44-b512-1370f02d74de": "red",
        "a495bb60-c5b1-4b44-b512-1370f02d74de": "blue",
        "a495bb50-c5b1-4b44-b512-1370f02d74de": "orange",
        "a495bb70-c5b1-4b44-b512-1370f02d74de": "pink",
        "a495bb40-c5b1-4b44-b512-1370f02d74de": "purple"
    }

colors_to_uuid = dict((v, k) for k, v in uuid_to_colors.items())

# Load config
parser = argparse.ArgumentParser(description='')
parser.add_argument('--simulate-beacons', dest='simulate_beacons', action='store_true',
                    help='Creates simulated beacon signals for testing')

args = parser.parse_args()
# Load config from file, with defaults, and args
config = PitchConfig.load(vars(args))

all_providers = [
        PrometheusCloudProvider(config),
        FileCloudProvider(config),
        InfluxDbCloudProvider(config)
    ]

enabled_providers = list()

#############################################
#############################################


def pitch_main():
    start_message()
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

    if config.simulate_beacons:
        threading.Thread(name='background', target=simulate_beacons).start()
    else:
        scanner = BeaconScanner(beacon_callback)
        scanner.start()
        print("...started: Tilt scanner")

    print("Ready!  Listening for beacons")


def simulate_beacons():
    """Simulates Beacon scanning with fake events. Useful when testing or developing
    without a beacon, or on a platform with no Bluetooth support"""
    print("...started: Tilt Beacon Simulator")
    # Using Namespace to trick a dict into a 'class'
    fake_packet = argparse.Namespace(**{
        'uuid': colors_to_uuid['purple'],
        'major': 70,
        'minor': 1035
    })
    while True:
        beacon_callback(None, None, fake_packet, dict())
        time.sleep(1)


def beacon_callback(bt_addr, rssi, packet, additional_info):
    uuid = packet.uuid
    color = uuid_to_colors.get(uuid)
    if color:
        # iBeacon packets have major/minor attributes with data
        # major = degrees in F (int)
        # minor = gravity (int) - needs to be converted to float (e.g. 1035 -> 1.035)
        tilt_status = TiltStatus(color, packet.major, get_decimal_gravity(packet.minor), config)
        # Update in enabled providers
        for provider in enabled_providers:
            try:
                provider.update(tilt_status)
            except Exception as e:
                #todo: better logging of errors
                print(e)
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