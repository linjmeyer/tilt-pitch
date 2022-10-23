import unittest
from pitch.configuration import PitchConfig
from pitch.models import TiltStatus

class TiltStatusTests(unittest.TestCase):

    def setUp(self):
        self.config = PitchConfig({})

    def test_temp_low(self):
        tilt_status = TiltStatus("purple", self.config.temp_range_min - 1, 1.050, self.config)
        self.assertFalse(tilt_status.temp_valid, msg="Temp is greater than min")

    def test_temp_high(self):
        tilt_status = TiltStatus("purple", self.config.temp_range_max + 1, 1.050, self.config)
        self.assertFalse(tilt_status.temp_valid, msg="Temp is less than max")
        
    def test_gravity_low(self):
        tilt_status = TiltStatus("purple", 70, self.config.gravity_range_min - 0.001, self.config)
        self.assertFalse(tilt_status.gravity_valid, msg="Gravity is greater than min")

    def test_gravity_high(self):
        tilt_status = TiltStatus("purple", 70, self.config.gravity_range_max + 0.001, self.config)
        self.assertFalse(tilt_status.gravity_valid, msg="Gravity is less than max")
        

if __name__ == '__main__':
    unittest.main()