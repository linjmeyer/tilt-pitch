from ..models import TiltStatus
from ..abstractions import CloudProviderBase
from ..configuration import PitchConfig
from interface import implements
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS, WritePrecision


class InfluxDb2CloudProvider(implements(CloudProviderBase)):

    def __init__(self, config: PitchConfig):
        self.config = config
        self.str_name = "InfluxDb2 ({})".format(config.influxdb2_url)
        self.batch = list()

    def __str__(self):
        return self.str_name

    def start(self):
        self.client = InfluxDBClient(
            url=self.config.influxdb2_url,
            token=self.config.influxdb2_token,
            org=self.config.influxdb2_org,
            timeout=self.config.influxdb_timeout_seconds)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)

    def update(self, tilt_status: TiltStatus):
        self.batch.append(self.get_point(tilt_status))
        if len(self.batch) < self.config.influxdb_batch_size:
            return
        # Batch size has been met, update and clear
        self.write_api.write(
            bucket=self.config.influxdb2_bucket,
            record=self.batch,
            write_precision=WritePrecision.MS)
        self.batch.clear()

    def enabled(self):
        return (self.config.influxdb2_url)

    def get_point(self, tilt_status: TiltStatus):
        return {
            "measurement": "tilt",
            "tags": {
                "color": tilt_status.color,
                "name": tilt_status.name
            },
            "fields": {
                "temp_fahrenheit": tilt_status.temp_fahrenheit,
                "temp_celsius": tilt_status.temp_celsius,
                "gravity": tilt_status.gravity,
                "alcohol_by_volume": tilt_status.alcohol_by_volume,
                "apparent_attenuation": tilt_status.apparent_attenuation
            }
        }
