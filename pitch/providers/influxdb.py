from ..models import TiltStatus
from ..abstractions import CloudProviderBase
from ..configuration import PitchConfig
from interface import implements
from influxdb import InfluxDBClient


class InfluxDbCloudProvider(implements(CloudProviderBase)):

    def __init__(self, config: PitchConfig):
        self.config = config
        self.str_name = "InfluxDb ({}:{})".format(config.influxdb_hostname,config.influxdb_port)
        self.batch = list()

    def __str__(self):
        return self.str_name

    def start(self):
        self.client = InfluxDBClient(self.config.influxdb_hostname, 
                                     self.config.influxdb_port, 
                                     self.config.influxdb_username, 
                                     self.config.influxdb_password, 
                                     self.config.influxdb_database, 
                                     timeout=self.config.influxdb_timeout_seconds)

    def update(self, tilt_status: TiltStatus):
        self.batch.append(self.get_point(tilt_status))
        if len(self.batch) < self.config.influxdb_batch_size:
            return
        # Batch size has been met, update and clear
        self.client.write_points(self.batch)
        self.batch.clear()

    def enabled(self):
        return (self.config.influxdb_hostname)

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