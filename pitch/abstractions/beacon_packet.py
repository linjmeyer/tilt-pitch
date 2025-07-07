from dataclasses import dataclass

@dataclass
class BeaconPacket:
    uuid: str
    major: int
    minor: int