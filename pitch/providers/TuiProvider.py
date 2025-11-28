import time
import plotext as plt
from datetime import datetime
from typing import Dict
from pitch.abstractions import CloudProviderBase
from pitch.configuration import PitchConfig
from pitch.models import TiltStatus


class TuiColorState:
    def __init__(self, color):
        self.color = color
        self.times = []
        self.gravity = []
        self.temperature = []
        # Used to set Y min/max on chart, starts with defaults and adjust if
        # larger/lower values are seen
        self.gravity_lower_bound = 0.990
        self.gravity_upper_bound = 1.099
        self.temp_lower_bound = 40
        self.temp_upper_bound = 100

    def append(self, tilt_status: TiltStatus):
        self.times.append(datetime.now())
        self.gravity.append(tilt_status.gravity)
        self.temperature.append(tilt_status.temp_fahrenheit)
        # Adjust min/max Y values for charting
        if tilt_status.gravity >= self.gravity_upper_bound:
            self.gravity_upper_bound = tilt_status.gravity + 0.05
        if tilt_status.gravity <= self.gravity_lower_bound:
            self.gravity_lower_bound = tilt_status.gravity - 0.05
        if tilt_status.temp_fahrenheit >= self.temp_upper_bound:
            self.temp_upper_bound = tilt_status.temp_fahrenheit + 5
        if tilt_status.temp_fahrenheit <= self.temp_lower_bound:
            self.temp_lower_bound = tilt_status.temp_fahrenheit - 5


class TuiProvider(CloudProviderBase):

    def __init__(self, config: PitchConfig):
        self.str_name = "TUI"
        self.data: Dict[str, TuiColorState] = {}
        self._last_plot_time = time.time()

    def __str__(self):
        return self.str_name

    def start(self):
        pass

    def _set_state(self, tilt_status: TiltStatus):
        # first time seeing this color, add it to state
        if tilt_status.color not in self.data.keys():
            self.data[tilt_status.color] = TuiColorState(tilt_status.color)
        # Update state
        self.data[tilt_status.color].append(tilt_status)

    def update(self, tilt_status: TiltStatus):
        self._set_state(tilt_status)
        now = time.time()
        if now - self._last_plot_time < 5:  # redraw every 5 seconds max
            return
        self._last_plot_time = now

        plt.date_form("%d/%m/%Y")
        plt.clf()
        plt.theme('clear')
        plt.subplots(2, 1)
        # SG Chart
        plt.subplot(1)
        plt.date_form("d/m/Y H:M:S")
        plt.title("Gravity")

        for color, cstate in self.data.items():
            if len(cstate.times) < 2:
                continue
            gravity_color, _ = TuiProvider.get_colors_for(color)
            x_vals = [dt.strftime("%d/%m/%Y %H:%M:%S")
                      for dt in cstate.times]
            plt.plot(x_vals, cstate.gravity, label=f"{color}", color=gravity_color)
            plt.ylim(cstate.gravity_lower_bound, cstate.gravity_upper_bound)

        plt.show()

        # Temp Chart
        plt.subplot(2)
        plt.date_form("d/m/Y H:M:S")
        plt.title("Temperature")
        plt.ylim(40, 100)

        for color, cstate in self.data.items():
            if len(cstate.times) < 2:
                continue
            x_vals = [dt.strftime("%d/%m/%Y %H:%M:%S")
                      for dt in cstate.times]
            _, temp_color = TuiProvider.get_colors_for(color)
            plt.plot(x_vals, cstate.temperature, label=f"{color}", color=temp_color)
            plt.ylim(cstate.temp_lower_bound, cstate.temp_upper_bound)

        plt.show()

    # noinspection PyMethodMayBeStatic
    def enabled(self):
        return True

    @staticmethod
    def get_colors_for(color: str):
        """Return (gravity_color_hex, temp_color_hex) for a given Tilt color."""
        color = color.lower()

        color_map = {
            "red": ("red", "red+"),
            "green": ("green", "green+"),
            "orange": ("orange", "orange+"),  # closest match
            "blue": ("blue", "blue+"),
            "black": ("gray", "gray+"),
            "pink": ("magenta", "magenta+"),
            # https://github.com/piccolomo/plotext/blob/master/readme/aspect.md#colors
            "purple": (91, 93),
            "yellow": (220, 226),
            "simulated": ("green", 115),
        }

        return color_map.get(color, ("#444444", "#AAAAAA"))  # fallback: gray