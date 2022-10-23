# Payload docs are found by clicking the "info" button next to a fermenation device on grainfather.com
# {
#     "specific_gravity": 1.034, //this must be a numeric value
#     "temperature": 18, //this must be numeric
#     "unit": "celsius" || "fahrenheit" //supply the unit that matches the temperature you are sending
# }

from ..models import TiltStatus
from ..abstractions import CloudProviderBase
from ..configuration import PitchConfig
from ..rate_limiter import DeviceRateLimiter
from interface import implements
import requests
import json


class GrainfatherCustomStreamCloudProvider(implements(CloudProviderBase)):

    def __init__(self, config: PitchConfig):
        self.color_urls = GrainfatherCustomStreamCloudProvider._normalize_color_keys(config.grainfather_custom_stream_urls)
        self.temp_unit = GrainfatherCustomStreamCloudProvider._get_temp_unit(config)
        self.str_name = "Grainfather Custom URL"
        self.rate_limiter = DeviceRateLimiter(rate=1, period=(60 * 15))  # 15 minutes

    def __str__(self):
        return self.str_name

    def start(self):
        pass

    def update(self, tilt_status: TiltStatus):
        # Skip if this color doesn't have a grainfather URL assigned
        if tilt_status.color not in self.color_urls.keys():
            return
        url = self.color_urls[tilt_status.color]
        self.rate_limiter.approve(tilt_status.color)
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        payload = self._get_payload(tilt_status)
        result = requests.post(url, headers=headers, data=json.dumps(payload))
        result.raise_for_status()

    def enabled(self):
        return True if self.color_urls else False
    
    def _get_payload(self, tilt_status: TiltStatus):
        return {
            "specific_gravity": tilt_status.gravity,
            "temperature": self._get_temp_value(tilt_status),
            "unit": self.temp_unit
        }

    def _get_temp_value(self, tilt_status: TiltStatus):
        if self.temp_unit == "fahrenheit":
            return tilt_status.temp_fahrenheit
        else:
            return tilt_status.temp_celsius

    # takes dict of color->urls
    # returns dict with all colors in lowercase letters for easier matching later
    @staticmethod
    def _normalize_color_keys(color_urls):
        normalized_colors = dict()
        if color_urls is not None:
            for color in color_urls:
                normalized_colors[color.lower()] = color_urls[color]

        return normalized_colors

    @staticmethod
    def _get_temp_unit(config: PitchConfig):
        temp_unit = config.grainfather_temp_unit.upper()
        if temp_unit == "C":
            return "celsius"
        elif temp_unit == "F":
            return "fahrenheit"

        raise ValueError("Grainfather temp unit must be F or C")

