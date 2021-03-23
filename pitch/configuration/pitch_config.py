import json
import os


class PitchConfig:

    def __init__(self, data: dict):
        # Queue
        self.queue_size = 3
        self.queue_empty_sleep_seconds = 1
        # Broadcast Data ranges
        self.temp_range_min = 32
        self.temp_range_max = 212
        self.gravity_range_min = 0.7
        self.gravity_range_max = 1.4
        # Webhook
        self.webhook_urls = list()
        self.webhook_limit_rate = 1
        self.webhook_limit_period = 1
        # File Path
        self.log_file_path = 'pitch_log.json'
        self.log_file_max_mb = 10
        # Prometheus
        self.prometheus_enabled = True
        self.prometheus_port = 8000
        # InfluxDB
        self.influxdb_hostname = None
        self.influxdb_database = None
        self.influxdb_port = None
        self.influxdb_username = None
        self.influxdb_password = None
        self.influxdb_batch_size = 10
        self.influxdb_timeout_seconds = 5
        # Brewfather
        self.brewfather_custom_stream_url = None
        self.brewfather_custom_stream_temp_unit = "F"
        # Brewersfriend
        self.brewersfriend_api_key = None
        self.brewersfriend_temp_unit = "F"
        # Grainfather
        self.grainfather_custom_stream_urls = None
        self.grainfather_temp_unit = "F"
        # Load user inputs from config file
        self.update(data)

    def update(self, data: dict):
        self.__dict__.update(data)

    def get_original_gravity(self, color: str):
        return self.__dict__.get(color + '_original_gravity')

    def get_gravity_offset(self, color: str):
        return self.__dict__.get(color + '_gravity_offset', 0)

    def get_temp_offset(self, color: str):
        return self.__dict__.get(color + '_temp_offset', 0)

    def get_brew_name(self, color: str):
        return self.__dict__.get(color + '_name', color)


    @staticmethod
    def load(additional_config: dict = None):
        file_path = "pitch.json"
        config_raw = dict()

        if os.path.isfile(file_path):
            file_open = open(file_path, "r").read()
            config_raw = json.loads(file_open)

        config = PitchConfig(config_raw)
        if additional_config is not None:
            config.update(additional_config)

        return config

