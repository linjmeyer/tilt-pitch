from ..rate_limiter import DeviceRateLimiter
from ..models import TiltStatus
from ..abstractions import CloudProviderBase
from ..configuration import PitchConfig
import requests


class WebhookCloudProvider(CloudProviderBase):

    def __init__(self, url, config: PitchConfig):
        self.url = url
        self.str_name = "Webhook ({})".format(url)
        self.rate_limiter = DeviceRateLimiter(rate=config.webhook_limit_rate, period=config.webhook_limit_period)
        self.timeout_seconds = config.http_timeout_seconds

    def __str__(self):
        return self.str_name

    def start(self):
        pass

    def update(self, tilt_status: TiltStatus):
        self.rate_limiter.approve(tilt_status.color)
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        requests.post(self.url, headers=headers, data=tilt_status.json(), timeout=self.timeout_seconds)

    def enabled(self):
        return True
