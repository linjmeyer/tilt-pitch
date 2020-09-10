from .json_serialize import JsonSerialize

class TiltStatus(JsonSerialize):

    def __init__(self, color, temp_f, gravity):
        self.color = color
        self.temp_f = temp_f
        self.temp_c = TiltStatus.get_celcius(temp_f)
        self.gravity = gravity

    @staticmethod
    def get_celcius(temp_f):
        return round((temp_f - 32) * 5.0/9.0)