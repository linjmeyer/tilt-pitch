from .json_serialize import JsonSerialize
from .tilt_status import TiltStatus

import socket

class WebhookPayload(JsonSerialize):
    def __init__(self, tilt: TiltStatus):
        self.tilt = tilt
        self.hostname = socket.gethostname()