import argparse
import random
import signal
import threading
import time
from queue import Queue

from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

from .configuration import PitchConfig
from .models import TiltStatus
from .providers import (InfluxDb2CloudProvider, InfluxDbCloudProvider,
                        WebhookCloudProvider)
from .rate_limiter import RateLimitedException

#############################################
# Statics
#############################################
uuid_to_colors = {
    "a495bb70-c5b1-4b44-b512-1370f02d74de": "yellow",
}

colors_to_uuid = dict((v, k) for k, v in uuid_to_colors.items())

# Load config from file, with defaults, and args
config = PitchConfig.load()

normal_providers = [
    InfluxDbCloudProvider(config),
    InfluxDb2CloudProvider(config),
]

# Queue for holding incoming scans
pitch_q: Queue = Queue(maxsize=config.queue_size)

#############################################
#############################################


def pitch_main(providers, timeout_seconds: int, simulate_beacons: bool, console_log: bool = True):
    if providers is None:
        providers = normal_providers

    # add any webhooks defined in config
    webhook_providers = _get_webhook_providers(config)
    if webhook_providers:
        providers.extend(webhook_providers)
    # Start cloud providers
    print("Starting...")
    enabled_providers = list()
    for provider in providers:
        if provider.enabled():
            enabled_providers.append(provider)
            provider__start_message = provider.start()
            if not provider__start_message:
                provider__start_message = ''
            print(f"...started: {provider} {provider__start_message}")
    # Start
    _start_scanner(enabled_providers, timeout_seconds,
                   simulate_beacons, console_log)


def _start_scanner(enabled_providers: list, timeout_seconds: int, simulate_beacons: bool, console_log: bool):
    if simulate_beacons:
        # Set daemon true so this thread dies when the parent process/thread dies
        threading.Thread(name='background',
                         target=_start_beacon_simulation, daemon=True).start()
    else:
        scanner = Beacon(_beacon_callback, packet_filter=IBeaconAdvertisement)
        scanner.start()
        signal.signal(signal.SIGTERM, _trigger_graceful_termination)
        print("...started: Tilt scanner")

    print("Ready!  Listening for beacons")
    start_time = time.time()
    end_time = start_time + timeout_seconds
    try:
        while True:
            time.sleep(0.01)
            _handle_pitch_queue(enabled_providers, console_log)
            # check timeout
            if timeout_seconds:
                current_time = time.time()
                if current_time > end_time:
                    return  # stop
    except KeyboardInterrupt:
        if not simulate_beacons:
            scanner.stop()
        print("...stopped: Tilt Scanner (keyboard interrupt)")
    except Exception as ex:
        if not simulate_beacons:
            scanner.stop()
        print(f"...stopped: Tilt Scanner ({ex})")


def _start_beacon_simulation():
    """Simulates Beacon scanning with fake events. Useful when testing or developing
    without a beacon, or on a platform with no Bluetooth support"""
    print("...started: Tilt Beacon Simulator")
    # Using Namespace to trick a dict into a 'class'
    while True:
        fake_packet = argparse.Namespace(**{
            'uuid': colors_to_uuid['simulated'],
            'major': random.randrange(65, 75),  # nosec: B311
            'minor': random.randrange(1035, 1040)  # nosec: B311
        })
        _beacon_callback(None, None, fake_packet, dict())
        time.sleep(0.25)


def _beacon_callback(bt_addr, rssi, packet, additional_info):
    # When queue is full broadcasts should be ignored
    # this can happen because Tilt broadcasts very frequently, while Pitch must make network calls
    # to forward Tilt status info on and this can cause Pitch to fall behind
    if pitch_q.full():
        return

    uuid = packet.uuid
    color = uuid_to_colors.get(uuid)
    if color:
        # iBeacon packets have major/minor attributes with data
        # major = degrees in F (int)
        # minor = gravity (int) - needs to be converted to float (e.g. 1035 -> 1.035)
        tilt_status = TiltStatus(
            color, packet.major, _get_decimal_gravity(packet.minor), config)
        if not tilt_status.temp_valid:
            print(f"Ignoring broadcast due to invalid temperature: {tilt_status.temp_fahrenheit}F")
        elif not tilt_status.gravity_valid:
            print(f"Ignoring broadcast due to invalid gravity: {str(tilt_status.gravity)}")
        else:
            pitch_q.put_nowait(tilt_status)


def _handle_pitch_queue(enabled_providers: list, console_log: bool):
    if config.queue_empty_sleep_seconds > 0 and pitch_q.empty():
        time.sleep(config.queue_empty_sleep_seconds)
        return

    if pitch_q.full():
        length = pitch_q.qsize()
        print(f"Queue is full ({length} events), scans will be ignored until the queue is reduced")

    tilt_status = pitch_q.get()
    for provider in enabled_providers:
        try:
            start = time.time()
            provider.update(tilt_status)
            time_spent = time.time() - start
            if console_log:
                print(f"Updated provider {provider} for color {tilt_status.color} took {time_spent:.3f} seconds")
        except RateLimitedException:
            # nothing to worry about, just called this too many times (locally)
            print(f"Skipping update due to rate limiting for provider {provider} for color {tilt_status.color}")
        except Exception as ex:
            # todo: better logging of errors
            print(ex)
    # Log it to console/stdout
    if console_log:
        print(tilt_status.json())


def _get_decimal_gravity(gravity):
    # gravity will be an int like 1035
    # turn into decimal, like 1.035
    return gravity * .001


def _get_webhook_providers(pitch_config: PitchConfig):
    # Multiple webhooks can be fired, so create them dynamically and add to
    # all providers static list
    webhook_providers = list()
    for url in pitch_config.webhook_urls:
        webhook_providers.append(WebhookCloudProvider(url, pitch_config))
    return webhook_providers


def _trigger_graceful_termination(signal_number, frame):
    raise Exception("Termination signal received")
