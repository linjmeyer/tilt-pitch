from typing import List
from influxdb_client import InfluxDBClient, WriteApi
from influxdb_client.client.write_api import SYNCHRONOUS, WritePrecision
from interface import implements

from ..abstractions import CloudProviderBase
from ..configuration import PitchConfig
from ..models import TiltStatus


class InfluxDb2CloudProvider(implements(CloudProviderBase)):

    def __init__(self, config: PitchConfig) -> None:
        self.config: PitchConfig = config
        if not self.config.influxdb2_url:
            self.config.influxdb2_url = ""
        self.str_name: str = f"InfluxDb2 ({config.influxdb2_url})"
        self.batch: List = []
        self.write_api: WriteApi = None
        self.client: InfluxDBClient = None

    def __str__(self) -> str:
        return self.str_name

    def start(self) -> None:
        self.client = InfluxDBClient(
            url=self.config.influxdb2_url,
            token=self.config.influxdb2_token,
            org=self.config.influxdb2_org)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)

    def update(self, tilt_status: TiltStatus) -> None:
        self.batch.append(self.get_point(tilt_status))
        if len(self.batch) < self.config.influxdb_batch_size:
            return
        # Batch size has been met, update and clear
        self.write_api.write(
            bucket=self.config.influxdb2_bucket,
            record=self.batch,
            write_precision=WritePrecision.MS)
        self.batch.clear()

    def enabled(self) -> str:
        return self.config.influxdb2_url

    def get_point(self, tilt_status: TiltStatus) -> dict:
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
