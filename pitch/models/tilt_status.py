from ..configuration import PitchConfig
from .json_serialize import JsonSerialize
import datetime


class TiltStatus(JsonSerialize):

    def __init__(self, color, temp_fahrenheit, current_gravity, config: PitchConfig):
        self.timestamp = datetime.datetime.now()
        self.color = color
        self.name = config.get_brew_name(color)
        self.temp_fahrenheit = temp_fahrenheit + config.get_temp_offset(color)
        self.temp_celsius = TiltStatus.get_celsius(temp_fahrenheit)
        self.original_gravity = config.get_original_gravity(color)
        self.gravity = current_gravity + config.get_gravity_offset(color)
        self.alcohol_by_volume = TiltStatus.get_alcohol_by_volume(self.original_gravity, self.gravity)
        self.apparent_attenuation = TiltStatus.get_apparent_attenuation(self.original_gravity, self.gravity)
        self.temp_valid = (config.temp_range_min < self.temp_fahrenheit and self.temp_fahrenheit < config.temp_range_max)
        self.gravity_valid = (config.gravity_range_min < self.gravity and self.gravity < config.gravity_range_max)

    @staticmethod
    def get_celsius(temp_fahrenheit):
        return round((temp_fahrenheit - 32) * 5.0/9.0)

    @staticmethod
    def get_alcohol_by_volume(original_gravity, current_gravity):
        if original_gravity is None:
            return 0
        alcohol_by_volume = (original_gravity - current_gravity) * 131.25
        return round(alcohol_by_volume, 2)

    @staticmethod
    def get_apparent_attenuation(original_gravity, current_gravity):
        if original_gravity is None:
            return 0
        aa = ((original_gravity - current_gravity) / original_gravity) * 2 * 1000
        return round(aa, 2)

    @staticmethod
    def get_gravity_points(gravity):
        """Converts gravity reading like 1.035 to just 35"""
