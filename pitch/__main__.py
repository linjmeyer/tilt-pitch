from . import pitch_main
from .providers import CalibrationCloudProvider
import argparse


def _get_args():
    # Load config
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--simulate-beacons', dest='simulate_beacons', action='store_true',
                        help='Creates simulated beacon signals for testing')
    parser.add_argument('--calibrate', dest='calibrate', action='store', default=None,
                        help='Color of the Tilt which Pitch will recommend calibrated values for temp (f) and gravity')
    parser.add_argument('--actual-temp', dest='actual_temp', action='store', default=0,
                        type=int, help='Measured temperature in degrees F, for used with calibrate flag')
    parser.add_argument('--actual-gravity', dest='actual_gravity', action='store', default=0,
                        type=float, help='Measured gravity, for used with calibrate flag')

    return parser.parse_args()


if __name__ == '__main__':
    args = _get_args()

    if args.calibrate:
        # Run with only calibration provider, timeout and disable output of json logs to console
        calibrator = CalibrationCloudProvider(args.calibrate, args.actual_temp, args.actual_gravity)
        pitch_main(providers=[calibrator],
                   timeout_seconds=5,
                   simulate_beacons=args.simulate_beacons,
                   console_log=False)
        print("Finished")
    else:
        # Run with default providers, forever, possibly simulating beacons
        pitch_main(providers=None, timeout_seconds=0, simulate_beacons=args.simulate_beacons)


