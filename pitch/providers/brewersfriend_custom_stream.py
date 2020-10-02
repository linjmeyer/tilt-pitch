# Payload docs: https://docs.brewersfriend.com/api/stream
# {
#  "name": "BrewBench",
#  "temp": 22.2,
#  "temp_unit": "C",
#  "gravity": 14.1,
#  "gravity_unit": "P",
#  "ph": 4.5,
#  "comment": "",
#  "beer": "",
#  "battery": 3.588112,
#  "RSSI": -57,
#  "angle": ""
# }

from ..models import TiltStatus
from ..abstractions import CloudProviderBase
from ..configuration import PitchConfig
from ..rate_limiter import DeviceRateLimiter
from interface import implements
import requests
import json


class BrewersFriendCustomStreamCloudProvider(implements(CloudProviderBase)):

    def __init__(self, config: PitchConfig):
        self.api_key = config.brewersfriend_api_key
        self.url = "https://log.brewersfriend.com/stream/{}".format(config.brewersfriend_api_key)
        self.str_name = "Brewer's Friend ({})".format(self.url)
        self.rate_limiter = DeviceRateLimiter(rate=1, period=(60 * 15))  # 15 minutes
        self.headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        self.temp_unit = BrewersFriendCustomStreamCloudProvider._get_temp_unit(config)

    def __str__(self):
        return self.str_name

    def start(self):
        pass

    def update(self, tilt_status: TiltStatus):
        self.rate_limiter.approve(tilt_status.color)
        payload = self._get_payload(tilt_status)
        result = requests.post(self.url, headers=self.headers, data=json.dumps(payload))
        result.raise_for_status()

    def enabled(self):
        return True if self.api_key else False

    def _get_payload(self, tilt_status: TiltStatus):
        return {
            'name': "Pitch-Tilt-" + tilt_status.color,
            'device_source': "tilt",
            'gravity': tilt_status.gravity,
            'og': tilt_status.original_gravity,
            'beer': tilt_status.name,
            'temp_unit': self.temp_unit,
            'temp': self._get_temp_value(tilt_status),
            'gravity_unit': "G"
        }

    def _get_temp_value(self, tilt_status: TiltStatus):
        if self.temp_unit == "F":
            return tilt_status.temp_fahrenheit
        else:
            return tilt_status.temp_celsius

    @staticmethod
    def _get_temp_unit(config: PitchConfig):
        temp_unit = config.brewersfriend_temp_unit.upper()
        if temp_unit in ["C", "F"]:
            return temp_unit

        raise ValueError("Brewer's Friend temp unit must be F or C")

