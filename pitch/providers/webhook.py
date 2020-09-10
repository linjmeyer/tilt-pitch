from ..models import TiltStatus
from ..abstractions import CloudProviderBase
from interface import implements
import requests

class WebhookCloudProvider(implements(CloudProviderBase)):

    def __str__(self):
        return "Webhook"

    def start(self):
        pass

    def update(self, tilt_status: TiltStatus):
        url = 'http://httpbin.org/anything'
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        requests.post(url, data=tilt_status.json())

    def enabled(self):
        return True