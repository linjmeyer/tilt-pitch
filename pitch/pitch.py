import signal
import threading
import time
import queue
import uuid as _uuid
import asyncio
from random import randrange
from .abstractions.beacon_packet import BeaconPacket
from .models import TiltStatus
from .providers import *
from .configuration import PitchConfig
from .providers.TuiProvider import TuiProvider
from .rate_limiter import RateLimitedException
from pyfiglet import Figlet
from bleak import BleakScanner

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
config: PitchConfig = PitchConfig.load()

normal_providers = [
        PrometheusCloudProvider(config),
        FileCloudProvider(config),
        BrewfatherCustomStreamCloudProvider(config),
        BrewersFriendCustomStreamCloudProvider(config),
        GrainfatherCustomStreamCloudProvider(config),
        TaplistIOCloudProvider(config),
        AzureIoTHubCloudProvider(config),
        SqliteCloudProvider(config)
    ]

# Queue for holding incoming scans
pitch_q = queue.Queue(maxsize=config.queue_size)

#############################################
#############################################


def pitch_main(providers, timeout_seconds: int, simulate_beacons: bool, tui_enabled: bool = False, console_log: bool = True):
    if providers is None:
        providers = normal_providers
    if tui_enabled:
        providers.append(TuiProvider(config))

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
        # Start BLE scanning thread using Bleak
        stop_event = threading.Event()
        # Trigger stop_event on termination signal
        signal.signal(signal.SIGTERM, lambda signalNumber, frame: stop_event.set())
        threading.Thread(target=_bleak_scanner_thread, args=(stop_event,), daemon=True).start()

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
        # BLE scanning thread will be terminated when program exits
        print("...stopped: Tilt Scanner (keyboard interrupt)")
    except Exception as e:
        # BLE scanning thread will be terminated when program exits
        print("...stopped: Tilt Scanner ({})".format(e))


def _start_beacon_simulation():
    """Simulates Beacon scanning with fake events. Useful when testing or developing
    without a beacon, or on a platform with no Bluetooth support"""
    print("...started: Tilt Beacon Simulator")
    temp_f = 71  #
    gravity_sg = 1.055
    step_temp = -0.05
    step_grav = 0.00005
    uuid = colors_to_uuid['simulated']
    while True:
        # If we are at the max ranges, swap the step to go in the opposite direction
        # this gives us some nice yo-yo-ing in the graph for effect
        if temp_f <= config.temp_range_min or temp_f >= config.temp_range_max:
            step_temp = step_temp * -1
        if gravity_sg <= config.gravity_range_min or gravity_sg >= config.gravity_range_max:
            step_grav = step_grav * -1
        fake_packet = BeaconPacket(
            uuid=uuid,
            major=int(temp_f),  # e.g. 67
            minor=int(gravity_sg * 1000),  # e.g. 1034
        )
        _beacon_callback(fake_packet)
        temp_f -= step_temp
        gravity_sg -= step_grav
        time.sleep(0.5)


def _beacon_callback(packet: BeaconPacket):
    uuid = packet.uuid
    color = uuid_to_colors.get(uuid)
    if color:
        # iBeacon packets have major/minor attributes with data
        # major = degrees in F (int)
        # minor = gravity (int) - needs to be converted to float (e.g. 1035 -> 1.035)
        temp_f = packet.major
        gravity = _get_decimal_gravity(packet.minor)
        tilt_status = TiltStatus(color, temp_f, gravity, config)
        if not tilt_status.temp_valid:
            print("Ignoring broadcast due to invalid temperature: {}F".format(tilt_status.temp_fahrenheit))
        elif not tilt_status.gravity_valid:
            print("Ignoring broadcast due to invalid gravity: " + str(tilt_status.gravity))
        elif pitch_q.full():
            print(f"Queue is full, skipping broadcast ({pitch_q.unfinished_tasks}/{pitch_q.maxsize})")
            return
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
            if console_log:
                print("Skipping update due to rate limiting for provider {} for color {}".format(provider, tilt_status.color))
        except Exception as e:
            if console_log:
                print("Skipping update due to rate limiting for provider {} for color {}".format(provider,
                                                                                                 tilt_status.color))
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
    
def _bleak_scanner_thread(stop_event):
    """
    Thread target to run BleakScanner event loop for BLE scanning.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(_bleak_scanner_loop(stop_event))

async def _bleak_scanner_loop(stop_event):
    """
    Asynchronous scanning loop running BleakScanner.
    """
    # Create scanner with detection callback (Bleak >=0.20 API)
    try:
        # Pass callback to constructor for newer Bleak versions
        scanner = BleakScanner(detection_callback=_bleak_detection_callback)
    except TypeError:
        # Fallback for older Bleak versions supporting register_detection_callback
        scanner = BleakScanner()
        scanner.register_detection_callback(_bleak_detection_callback)
    await scanner.start()
    print("...started: Tilt scanner")
    try:
        while not stop_event.is_set():
            await asyncio.sleep(1.0)
    finally:
        await scanner.stop()


def _bleak_detection_callback(_, advertisement_data):
    """
    Detection callback for BleakScanner.
    Parses iBeacon manufacturer data and forwards to _beacon_callback.
    """
    md = advertisement_data.manufacturer_data
    if not md:
        return
    # Apple Company ID for iBeacon is 0x004C
    ib = md.get(76)
    if not ib or len(ib) < 23:
        return
    # Confirm iBeacon prefix: 0x02, 0x15
    if ib[0] != 0x02 or ib[1] != 0x15:
        return
    # Extract UUID from bytes 2-17
    uuid_str = str(_uuid.UUID(bytes=bytes(ib[2:18])))
    # Extract major (bytes 18-19) and minor (bytes 20-21)
    major = int.from_bytes(ib[18:20], byteorder='big')
    minor = int.from_bytes(ib[20:22], byteorder='big')
    packet =  BeaconPacket(uuid=uuid_str, major=major, minor=minor)
    _beacon_callback(packet)
