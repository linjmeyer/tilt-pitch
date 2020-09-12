from ..configuration import PitchConfig
from .json_serialize import JsonSerialize
import datetime


class TiltStatus(JsonSerialize):

    def __init__(self, color, temp_f, current_gravity, config: PitchConfig):
        self.timestamp = datetime.datetime.now()
        self.color = color
        self.temp_f = temp_f
        self.temp_c = TiltStatus.get_celcius(temp_f)
        self.gravity = current_gravity
        self.abv = TiltStatus.get_abv(color, current_gravity, config)


    @staticmethod
    def get_celcius(temp_f):
        return round((temp_f - 32) * 5.0/9.0)

    @staticmethod
    def get_abv(color, current_gravity, config: PitchConfig):
        original_gravity = config.get_original_gravity(color)
        if original_gravity is None:
            return 0
        abv = (original_gravity - current_gravity) * 131.25
        return round(abv, 2)
