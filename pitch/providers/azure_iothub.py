from ..models import TiltStatus
from ..abstractions import CloudProviderBase
from interface import implements
from ..configuration import PitchConfig
from ..rate_limiter import DeviceRateLimiter
import requests
from azure.iot.device import IoTHubSession, MQTTError, MQTTConnectionFailedError
import json
import asyncio


class AzureIoTHubCloudProvider(implements(CloudProviderBase)):

    def __init__(self, config: PitchConfig):
        self.config = config
        self.str_name = "Azure IoT Hub ({})".format(config.azure_iot_hub_connectionstring)
        self.rate_limiter = DeviceRateLimiter(rate=config.azure_iot_hub_limit_rate, period=config.azure_iot_hub_limit_period)

    def __str__(self):
        return self.str_name

    def start(self):
        pass

    async def send(self, tilt_status: TiltStatus):        
        try:
            async with IoTHubSession.from_connection_string(self.config.azure_iot_hub_connectionstring) as session:
                await session.send_message(tilt_status.json())
        except MQTTError as e:
            print(f"Connection to IoT Hub dropped: {e}")
        except MQTTConnectionFailedError as e:
            print(f"Could not connect to IoT Hub: {e}.")

    def update(self, tilt_status: TiltStatus):
        self.rate_limiter.approve(tilt_status.color)
        asyncio.run(self.send(tilt_status))

    def enabled(self):
        enabled = True if self.config.azure_iot_hub_connectionstring else False
        return enabled
