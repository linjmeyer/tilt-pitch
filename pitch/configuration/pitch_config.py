import json

class PitchConfig:

    def __init__(self, data: dict):
        # Webhook
        self.webhook_urls = list()
        # File Path
        self.log_file_path = None
        self.log_file_max_mb = 10
        # Load user inputs from config file
        self.__dict__.update(data)


    @staticmethod
    def load():
        file_path = "pitch.json"
        file_open = open(file_path, "r").read()
        config_raw = json.loads(file_open)
        return PitchConfig(config_raw)

