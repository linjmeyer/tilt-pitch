from ..configuration import PitchConfig
from .json_serialize import JsonSerialize
import datetime


class TiltStatus(JsonSerialize):

    def __init__(self, color, temp_f, current_gravity, config: PitchConfig):
        self.timestamp = datetime.datetime.now()
        self.color = color
        self.temp_f = temp_f
        self.temp_c = TiltStatus.get_celsius(temp_f)
        self.original_gravity = config.get_original_gravity(color)
        self.gravity = current_gravity
        self.abv = TiltStatus.get_abv(self.original_gravity, current_gravity)
        self.apparent_attenuation = TiltStatus.get_apparent_attenuation(self.original_gravity, current_gravity)

    @staticmethod
    def get_celsius(temp_f):
        return round((temp_f - 32) * 5.0/9.0)

    @staticmethod
    def get_abv(original_gravity, current_gravity):
        if original_gravity is None:
            return 0
        abv = (original_gravity - current_gravity) * 131.25
        return round(abv, 2)

    @staticmethod
    def get_apparent_attenuation(original_gravity, current_gravity):
        if original_gravity is None:
            return 0
        aa = ((original_gravity - current_gravity) / original_gravity) * 2 * 1000
        return round(aa, 2)

    @staticmethod
    def get_gravity_points(gravity):
        """Converts gravity reading like 1.035 to just 35"""
