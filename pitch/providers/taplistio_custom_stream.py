from ..models import TiltStatus
from ..abstractions import CloudProviderBase
from ..configuration import PitchConfig
from ..rate_limiter import DeviceRateLimiter
from interface import implements
import requests
import json


class TaplistIOCloudProvider(implements(CloudProviderBase)):
    def __init__(self, config: PitchConfig):
        self.url = config.taplistio_url
        self.str_name = "Taplist.io ({})".format(self.url)
        self.rate_limiter = DeviceRateLimiter(rate=1, period=(60 * 15))  # 15 minutes

    def __str__(self):
        return self.str_name

    def start(self):
        pass

    def update(self, tilt_status: TiltStatus):
        self.rate_limiter.approve(tilt_status.color)
        headers = {
            'Content-type': 'application/json',
            'User-Agent': 'tilt-pitch',
        }
        payload = self._get_payload(tilt_status)
        result = requests.post(self.url, headers=headers, data=json.dumps(payload))
        result.raise_for_status()

    def enabled(self):
        return True if self.url else False

    def _get_payload(self, tilt_status: TiltStatus):
        return {
            'Color': tilt_status.color,
            'Temp': tilt_status.temp_fahrenheit,
            'SG': tilt_status.gravity,
            'temperature_unit': 'F',
            'gravity_unit': 'G'
        }
