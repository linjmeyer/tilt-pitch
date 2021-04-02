import argparse
import signal
import threading
import time
import queue
import logging
from pyfiglet import Figlet
from beacontools import BeaconScanner, IBeaconAdvertisement
from .models import TiltStatus
from .providers import *
from .configuration import PitchConfig
from .rate_limiter import RateLimitedException

#############################################
# Statics
#############################################
uuid_to_colors = {
        "a495bb20-c5b1-4b44-b512-1370f02d74de": "green",
        "a495bb30-c5b1-4b44-b512-1370f02d74de": "black",
        "a495bb10-c5b1-4b44-b512-1370f02d74de": "red",
        "a495bb60-c5b1-4b44-b512-1370f02d74de": "blue",
        "a495bb50-c5b1-4b44-b512-1370f02d74de": "orange",
        "a495bb70-c5b1-4b44-b512-1370f02d74de": "yellow",
        "a495bb40-c5b1-4b44-b512-1370f02d74de": "purple",
        "a495bb80-c5b1-4b44-b512-1370f02d74de": "pink",
        "a495bb40-c5b1-4b44-b512-1370f02d74df": "simulated"  # reserved for fake beacons during simulation mode
    }

colors_to_uuid = dict((v, k) for k, v in uuid_to_colors.items())

# Load config from file, with defaults, and args
config = PitchConfig.load()

normal_providers = [
        PrometheusCloudProvider(config),
        FileCloudProvider(config),
        InfluxDbCloudProvider(config),
        BrewfatherCustomStreamCloudProvider(config),
        BrewersFriendCustomStreamCloudProvider(config),
        GrainfatherCustomStreamCloudProvider(config)
    ]

# Queue for holding incoming scans
pitch_q = queue.Queue(maxsize=config.queue_size)

#############################################
#############################################


def pitch_main(providers, timeout_seconds: int, simulate_beacons: bool, console_log: bool = True):
    if providers is None:
        providers = normal_providers

    _start_message()
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
            print("...started: {} {}".format(provider, provider__start_message))
    # Start
    _start_scanner(enabled_providers, timeout_seconds, simulate_beacons, console_log)


def _start_scanner(enabled_providers: list, timeout_seconds: int, simulate_beacons: bool, console_log: bool):
    if simulate_beacons:
        # Set daemon true so this thread dies when the parent process/thread dies
        threading.Thread(name='background', target=_start_beacon_simulation, daemon=True).start()
    else:
        scanner = BeaconScanner(_beacon_callback,packet_filter=IBeaconAdvertisement)
        scanner.start()    
        signal.signal(signal.SIGTERM, _trigger_graceful_termination)
        print("...started: Tilt scanner")
        

    print("Ready!  Listening for beacons")
    start_time = time.time()
    end_time = start_time + timeout_seconds
    try:
        while True:
            _handle_pitch_queue(enabled_providers, console_log)
            # check timeout
            if timeout_seconds:
                current_time = time.time()
                if current_time > end_time:
                    return  # stop
    except KeyboardInterrupt as e:
        if not simulate_beacons:
            scanner.stop()
        print("...stopped: Tilt Scanner (keyboard interrupt)")
    except Exception as e:
        if not simulate_beacons:
            scanner.stop()
        print("...stopped: Tilt Scanner ({})".format(e))

def _start_beacon_simulation():
    """Simulates Beacon scanning with fake events. Useful when testing or developing
    without a beacon, or on a platform with no Bluetooth support"""
    print("...started: Tilt Beacon Simulator")
    # Using Namespace to trick a dict into a 'class'
    fake_packet = argparse.Namespace(**{
        'uuid': colors_to_uuid['simulated'],
        'major': 70,
        'minor': 1035
    })
    while True:
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
        tilt_status = TiltStatus(color, packet.major, _get_decimal_gravity(packet.minor), config)
        if not tilt_status.temp_valid:
            print("Ignoring broadcast due to invalid temperature: {}F".format(tilt_status.temp_fahrenheit))
        elif not tilt_status.gravity_valid:
            print("Ignoring broadcast due to invalid gravity: " + tilt_status.gravity)
        else:
            pitch_q.put_nowait(tilt_status)


def _handle_pitch_queue(enabled_providers: list, console_log: bool):
    if config.queue_empty_sleep_seconds > 0 and pitch_q.empty():
        time.sleep(config.queue_empty_sleep_seconds)
        return

    if pitch_q.full():
        length = pitch_q.qsize()
        print("Queue is full ({} events), scans will be ignored until the queue is reduced".format(length))

    tilt_status = pitch_q.get()
    for provider in enabled_providers:
        try:
            start = time.time()
            provider.update(tilt_status)
            time_spent = time.time() - start
            if console_log:
                print("Updated provider {} for color {} took {:.3f} seconds".format(provider, tilt_status.color, time_spent))
        except RateLimitedException:
            # nothing to worry about, just called this too many times (locally)
            print("Skipping update due to rate limiting for provider {} for color {}".format(provider, tilt_status.color))
        except Exception as e:
            # todo: better logging of errors
            print(e)
    # Log it to console/stdout
    if console_log:
        print(tilt_status.json())


def _get_decimal_gravity(gravity):
    # gravity will be an int like 1035
    # turn into decimal, like 1.035
    return gravity * .001


def _get_webhook_providers(config: PitchConfig):
    # Multiple webhooks can be fired, so create them dynamically and add to
    # all providers static list
    webhook_providers = list()
    for url in config.webhook_urls:
        webhook_providers.append(WebhookCloudProvider(url, config))
    return webhook_providers


def _start_message():
    f = Figlet(font='slant')
    print(f.renderText('Pitch'))

def _trigger_graceful_termination(signalNumber, frame):
    raise Exception("Termination signal received")