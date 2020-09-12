from ..models import TiltStatus
from ..abstractions import CloudProviderBase
from ..configuration import PitchConfig
from interface import implements
from influxdb import InfluxDBClient

class InfluxDbCloudProvider(implements(CloudProviderBase)):

    def __init__(self, config: PitchConfig):
        self.config = config
        self.str_name = "InfluxDb ({}:{})".format(config.influxdb_hostname,config.influxdb_port)

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
        points = self.get_points(tilt_status)
        self.client.write_points(points, batch_size=self.config.influxdb_batch_size)

    def enabled(self):
        return (self.config.influxdb_hostname)

    def get_points(self, tilt_status: TiltStatus):
        return [
            {
                "measurement": "tilt",
                "tags": {
                    "color": tilt_status.color
                },
                "fields": {
                    "temp_f": tilt_status.temp_f,
                    "temp_c": tilt_status.temp_c,
                    "gravity": tilt_status.gravity,
                    "abv": tilt_status.abv
                }
            }
        ]