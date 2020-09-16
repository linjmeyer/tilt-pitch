from ..models import TiltStatus
from ..abstractions import CloudProviderBase
from ..configuration import PitchConfig
from interface import implements
from prometheus_client import Counter, Gauge, start_http_server

counter_beacons_received = Counter('pitch_beacons_received', 'Number of beacons received', ['color', 'name'])
gauge_temperature_fahrenheit = Gauge('pitch_temperature_fahrenheit', 'Temperature in fahrenheit', ['color', 'name'])
gauge_temperature_celsius = Gauge('pitch_temperature_celsius', 'Temperature in celsius', ['color', 'name'])
gauge_gravity = Gauge('pitch_gravity', 'Gravity of the beer', ['color', 'name'])
gauge_alcohol_by_volume = Gauge('pitch_alcohol_by_volume', 'ABV of the beer', ['color', 'name'])
gauge_aa = Gauge('pitch_apparent_attenuation', 'Apparent attenuation of the beer', ['color', 'name'])


class PrometheusCloudProvider(implements(CloudProviderBase)):

    def __init__(self, config: PitchConfig):
        self.is_enabled = config.prometheus_enabled
        self.port = config.prometheus_port

    def __str__(self):
        return "Prometheus"

    def start(self):
        start_http_server(self.port)
        return "(http://127.0.0.1:{}/metrics)".format(self.port)

    def update(self, tilt_status: TiltStatus):
        counter_beacons_received.labels(color=tilt_status.color, name=tilt_status.name).inc()
        gauge_temperature_fahrenheit.labels(color=tilt_status.color, name=tilt_status.name).set(tilt_status.temp_fahrenheit)
        gauge_temperature_celsius.labels(color=tilt_status.color, name=tilt_status.name).set(tilt_status.temp_celsius)
        gauge_gravity.labels(color=tilt_status.color, name=tilt_status.name).set(tilt_status.gravity)
        gauge_alcohol_by_volume.labels(color=tilt_status.color, name=tilt_status.name).set(tilt_status.alcohol_by_volume)
        gauge_aa.labels(color=tilt_status.color, name=tilt_status.name).set(tilt_status.apparent_attenuation)

    def enabled(self):
        return self.is_enabled
