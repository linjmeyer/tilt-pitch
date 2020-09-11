import json

class PitchConfig:

    def __init__(self, data: dict):
        # Webhook
        self.webhook_urls = list()
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
        # Load user inputs from config file
        self.__dict__.update(data)


    @staticmethod
    def load():
        file_path = "pitch.json"
        file_open = open(file_path, "r").read()
        config_raw = json.loads(file_open)
        return PitchConfig(config_raw)

