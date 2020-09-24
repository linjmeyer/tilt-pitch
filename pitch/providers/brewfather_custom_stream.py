# Payload docs: https://docs.brewfather.app/integrations/custom-stream
# {
#   "name": "YourDeviceName", // Required field, this will be the ID in Brewfather
#   "temp": 20.32,
#   "aux_temp": 15.61, // Fridge Temp
#   "ext_temp": 6.51, // Room Temp
#   "temp_unit": "C", // C, F, K
#   "gravity": 1.042,
#   "gravity_unit": "G", // G, P
#   "pressure": 10,
#   "pressure_unit": "PSI", // PSI, BAR, KPA
#   "ph": 4.12,
#   "bpm": 123, // Bubbles Per Minute
#   "comment": "Hello World",
#   "beer": "Pale Ale"
# }

from ..models import TiltStatus
from ..abstractions import CloudProviderBase
from ..configuration import PitchConfig
from ..rate_limiter import DeviceRateLimiter
from interface import implements
import requests
import json


class BrewfatherCustomStreamCloudProvider(implements(CloudProviderBase)):

    def __init__(self, config: PitchConfig):
        self.url = config.brewfather_custom_stream_url
        self.temp_unit = BrewfatherCustomStreamCloudProvider._get_temp_unit(config)
        self.str_name = "Brewfather ({})".format(self.url)
        self.rate_limiter = DeviceRateLimiter(rate=1, period=(60 * 15))  # 15 minutes

    def __str__(self):
        return self.str_name

    def start(self):
        pass

    def update(self, tilt_status: TiltStatus):
        self.rate_limiter.approve(tilt_status.color)
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        payload = self._get_payload(tilt_status)
        result = requests.post(self.url, headers=headers, data=json.dumps(payload))
        result.raise_for_status()

    def enabled(self):
        return True if self.url else False

    def _get_temp_value(self, tilt_status: TiltStatus):
        if self.temp_unit == "F":
            return tilt_status.temp_fahrenheit
        else:
            return tilt_status.temp_celsius

    def _get_payload(self, tilt_status: TiltStatus):
        return {
            'name': "PitchTilt" + tilt_status.color,
            'beer': tilt_status.name,
            'temp': self._get_temp_value(tilt_status),
            'temp_unit': self.temp_unit,
            'gravity': tilt_status.gravity,
            'gravity_unity': "G"
        }

    @staticmethod
    def _get_temp_unit(config: PitchConfig):
        temp_unit = config.brewfather_custom_stream_temp_unit.upper()
        if temp_unit in ["C", "F"]:
            return temp_unit

        raise ValueError("Brewfather temp unit must be F or C")

