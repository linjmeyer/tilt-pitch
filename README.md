# Pitch (Tilt Hydrometer tool)

Pitch is an unofficial replacement for Tilt Hydrometer mobile apps and TiltPi software.  Tilt hardware is required.  It is designed to be easy to use and integrated with other tools like Promethues for metrics, or any generic third party source using webhooks.

# Why

The Tilt hardware is impressive, but the Android app, iOS app and TiltPi are clunky, confusing and buggy.  This project aims to provide a better more reliable solution, but is focused on more tech-savvy brewers than the official Tilt projects.  

# Features

* Webhooks for supporting generic integrations (similar to Tilt's Cloud Logging feature)
* Prometheus Metrics

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

ToDo: Configurable webhooks

Webhook payload format:

```
{
    "color": "purple",
    "temp_f": 69,
    "temp_c": 21,
    "gravity": 1.035
}
```

