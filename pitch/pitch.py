import asyncio
import signal
from construct import Array, Byte, Const, Int8sl, Int16ub, Struct
import time
from queue import Queue
from uuid import UUID

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
ibeacon_format = Struct(
    "type_length" / Const(b"\x02\x15"),
    "uuid" / Array(16, Byte),
    "temperature" / Int16ub,
    "gravity" / Int16ub,
    "power" / Int8sl,
)


#############################################
#############################################


def pitch_main(providers, timeout_seconds: int, console_log: bool = True):
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
    asyncio.run(_start_scanner(enabled_providers, timeout_seconds, console_log))


async def _start_scanner(enabled_providers: list, timeout_seconds: int, console_log: bool):
    scanner = BleakScanner()
    scanner.register_detection_callback(_beacon_callback)

    signal.signal(signal.SIGTERM, _trigger_graceful_termination)
    print("...started: Tilt scanner")

    print("Ready!  Listening for beacons")
    start_time = time.time()
    end_time = start_time + timeout_seconds
    try:
        while True:
            await scanner.start()
            await asyncio.sleep(1.0)
            await scanner.stop()

            _handle_pitch_queue(enabled_providers, console_log)
            # check timeout
            if timeout_seconds:
                current_time = time.time()
                if current_time > end_time:
                    return  # stop
    except KeyboardInterrupt:
        scanner.stop()
        print("...stopped: Tilt Scanner (keyboard interrupt)")
    except Exception as ex:
        scanner.stop()
        print(f"...stopped: Tilt Scanner ({ex})")


def _beacon_callback(_, advertisement_data: AdvertisementData):
    # When queue is full broadcasts should be ignored
    # this can happen because Tilt broadcasts very frequently, while Pitch must make network calls
    # to forward Tilt status info on and this can cause Pitch to fall behind
    try:
        manufacturer_data = advertisement_data.manufacturer_data[0x004C]
        ibeacon = ibeacon_format.parse(manufacturer_data)
        uuid: UUID = UUID(bytes=bytes(ibeacon.uuid))
        if uuid == UUID("a495bb70-c5b1-4b44-b512-1370f02d74de"):
            if pitch_q.full():
                return

            color = "yellow"
            if color:
                tilt_status = TiltStatus(color, ibeacon.temperature, _get_decimal_gravity(ibeacon.gravity), config)
                if not tilt_status.temp_valid:
                    print(f"Ignoring broadcast due to invalid temperature: {tilt_status.temp_fahrenheit}F")
                elif not tilt_status.gravity_valid:
                    print(f"Ignoring broadcast due to invalid gravity: {str(tilt_status.gravity)}")
                else:
                    pitch_q.put_nowait(tilt_status)
    except KeyError:
        pass


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
            # TODO: better logging of errors
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
    raise KeyboardInterrupt("Termination signal received")
