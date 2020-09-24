from ..rate_limiter import DeviceRateLimiter
from ..models import TiltStatus
from ..abstractions import CloudProviderBase
from interface import implements
from ..configuration import PitchConfig
import requests


class WebhookCloudProvider(implements(CloudProviderBase)):

    def __init__(self, url, config: PitchConfig):
        self.url = url
        self.str_name = "Webhook ({})".format(url)
        self.rate_limiter = DeviceRateLimiter(rate=config.webhook_limit_rate, period=config.webhook_limit_period)

    def __str__(self):
        return self.str_name

    def start(self):
        pass

    def update(self, tilt_status: TiltStatus):
        self.rate_limiter.approve(tilt_status.color)
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        requests.post(self.url, headers=headers, data=tilt_status.json())

    def enabled(self):
        return True
