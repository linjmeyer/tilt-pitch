import sqlite3
import threading
import time
from interface import implements
from ..abstractions import CloudProviderBase
from ..models import TiltStatus
from ..configuration import PitchConfig
from ..rate_limiter import DeviceRateLimiter


class SqliteCloudProvider(implements(CloudProviderBase)):
    """
    Persist TiltStatus updates into a local SQLite database (enabled by default).
    """
    def __init__(self, config: PitchConfig):
        # Default database file path
        self.db_path = getattr(config, 'sqlite_db_path', 'pitch.db')
        # Ensure only one thread initializes the DB
        self._lock = threading.Lock()
        self._rate_limiter = DeviceRateLimiter(rate=1, period=60)

    def __str__(self):
        return f"SQLite ({self.db_path})"

    def start(self):
        """
        Create the SQLite database and table if they don't exist.
        """
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute(
                '''
                CREATE TABLE IF NOT EXISTS fermentation_readings (
                    timestamp INTEGER,
                    color TEXT,
                    name TEXT,
                    temp_f REAL,
                    temp_c REAL,
                    gravity REAL,
                    abv REAL,
                    attenuation REAL
                );
                '''
            )
            conn.commit()
            conn.close()
        # no extra startup message
        return ''

    def update(self, tilt_status: TiltStatus):
        """
        Insert a new row for each TiltStatus.
        """
        # Tilt beacons can broadcast pretty quickly, but the values won't change often
        # We can ignore a lot of them and reduce size/query times in DB using a rate limiter
        self._rate_limiter.approve(tilt_status.color)
        # Use a new connection on each thread
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO fermentation_readings (timestamp, color, name, temp_f, temp_c, gravity, abv, attenuation) '
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (
                int(time.time()),
                tilt_status.color,
                tilt_status.name,
                tilt_status.temp_fahrenheit,
                tilt_status.temp_celsius,
                tilt_status.gravity,
                tilt_status.alcohol_by_volume,
                tilt_status.apparent_attenuation,
            )
        )
        conn.commit()
        conn.close()

    # noinspection PyMethodMayBeStatic
    def enabled(self):
        # Always enabled by default
        return True
