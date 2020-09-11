# Pitch (Tilt Hydrometer tool)

Pitch is an unofficial replacement for Tilt Hydrometer mobile apps and TiltPi software.  Tilt hardware is required.  It is designed to be easy to use and integrated with other tools like Promethues for metrics, or any generic third party source using webhooks.

# Why

The Tilt hardware is impressive, but the mobile apps and TiltPi are confusing and buggy.  This project aims to provide a better more reliable solution, but is focused on more tech-savvy brewers than the official Tilt projects.  

# Features

The following features are implemented, planned, or will be investigated in the future:

* [x] Track multiple Tilts at once
* [x] Prometheus Metrics
* [x] Tilt status log file (JSON)
* [ ] InfluxDB Metrics
* [ ] Multple logging and metric sources simultaneously
* [ ] Webhooks for supporting generic integrations (similar to Tilt's Cloud Logging feature)
* [ ] Brewing Cloud Services (Brewstats, Brewer's Friend, etc.)
* [ ] Google Sheets (using any Google Drive)


# Name

It's an unoffical tradition to name tech projects using nautical terms.  Pitch is a term used to describe the tilting/movement of a ship at sea.  Given pitching is also a brewing term, it seemed like a good fit.

# Integrations

## Prometheus Metrics

Prometheus metrics are hosted on port 8000.  For each Tilt the followed Prometheus metrics are created:

```
# HELP pitch_beacons_received_total Number of beacons received
# TYPE pitch_beacons_received_total counter
pitch_beacons_received_total{color="purple"} 3321.0

# HELP pitch_temperature_fahrenheit Temperature in fahrenheit
# TYPE pitch_temperature_fahrenheit gauge
pitch_temperature_fahrenheit{color="purple"} 69.0

# HELP pitch_temperature_celcius Temperature in celcius
# TYPE pitch_temperature_celcius gauge
pitch_temperature_celcius{color="purple"} 21.0

# HELP pitch_gravity Gravity of the beer
# TYPE pitch_gravity gauge
pitch_gravity{color="purple"} 1.035
```

## Webhook

Unlimited webhooks can be configured using the config option `webhook_urls`.  Each Tilt status broadcast will result in a webhook call to all URLs.

Webhooks are sent as HTTP POST with the following json payload:

```
{
    "color": "purple",
    "temp_f": 69,
    "temp_c": 21,
    "gravity": 1.035
}
```

## JSON Log File

Tilt status broadcast events can be logged to a json file using the config option `log_file_path`.  Each event is a newline.  Example file:

```
{"timestamp": "2020-09-11T02:15:30.525232", "color": "purple", "temp_f": 70, "temp_c": 21, "gravity": 0.997}
{"timestamp": "2020-09-11T02:15:32.539619", "color": "purple", "temp_f": 70, "temp_c": 21, "gravity": 0.997}
{"timestamp": "2020-09-11T02:15:33.545388", "color": "purple", "temp_f": 70, "temp_c": 21, "gravity": 0.997}
{"timestamp": "2020-09-11T02:15:34.548556", "color": "purple", "temp_f": 70, "temp_c": 21, "gravity": 0.997}
{"timestamp": "2020-09-11T02:15:35.557411", "color": "purple", "temp_f": 70, "temp_c": 21, "gravity": 0.997}
{"timestamp": "2020-09-11T02:15:36.562158", "color": "purple", "temp_f": 70, "temp_c": 21, "gravity": 0.996}
```

