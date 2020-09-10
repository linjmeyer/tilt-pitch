from interface import Interface
from ..models import TiltStatus

class CloudProviderBase(Interface):

    def start(self):
        pass

    def update(self, tilt_status: TiltStatus):
        pass

    def enabled(self):
        return False