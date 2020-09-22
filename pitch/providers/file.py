from ..models import TiltStatus
from ..abstractions import CloudProviderBase
from ..configuration import PitchConfig
from interface import implements
import logging
import logging.handlers


class FileCloudProvider(implements(CloudProviderBase)):

    def __init__(self, config: PitchConfig):
        self.config = config
        self.str_name = "File ({})".format(config.log_file_path)
        self.logger = logging.getLogger(self.str_name)

    def __str__(self):
        return self.str_name

    def start(self):
        maxBytes = self.config.log_file_max_mb * 1024 * 1024
        handler = logging.handlers.RotatingFileHandler(self.config.log_file_path, maxBytes=maxBytes)
        self.logger.addHandler(handler)

    def update(self, tilt_status: TiltStatus):
        self.logger.warning(tilt_status.json())

    def enabled(self):
        return (self.config.log_file_path)