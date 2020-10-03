from ..models import TiltStatus
from ..abstractions import CloudProviderBase
from interface import implements


class CalibrationCloudProvider(implements(CloudProviderBase)):

    def __init__(self, color: str, actual_temp: int = 0, actual_gravity: float = 0):
        self.color = color.lower()
        self.str_name = "Calibration ({})".format(self.color)
        self.actual_temp = actual_temp
        self.actual_gravity = actual_gravity
        if actual_temp <= 0 and actual_gravity <= 0:
            raise ValueError("Please provide actual_temp, actual_gravity, or both")

    def __str__(self):
        return self.str_name

    def start(self):
        pass

    def update(self, tilt_status: TiltStatus):
        if tilt_status.color == self.color:
            gravity_offset = self.actual_gravity - tilt_status.gravity
            temp_offset = self.actual_temp - tilt_status.temp_fahrenheit
            print("{}: gravity={}, gravity_offset={}; temp_f={}, temp_offset={}"
                  .format(tilt_status.color,
                          tilt_status.gravity, gravity_offset,
                          tilt_status.temp_fahrenheit, temp_offset))

    def enabled(self):
        return True
