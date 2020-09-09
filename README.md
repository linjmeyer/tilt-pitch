# Pitch (Tilt Hydrometer tool)

Pitch is an unofficial replacement for Tilt Hydrometer mobile apps and TiltPi software.  Tilt hardware is required.  It is designed to be easy to use and integrated with other tools like Promethues for metrics, or any generic third party source using webhooks.

# Why

The Tilt hardware is impressive, but the Android app, iOS app and TiltPi are clunky, confusing and buggy.  This project aims to provide a better more reliable solution, but is focused on more tech-savvy brewers than the official Tilt projects.  

# Features

* Webhooks for supporting generic integrations (similar to Tilt's Cloud Logging feature)
* Prometheus Metrics

# Name

It's an unoffical tradition to name tech projects using nautical terms.  Pitch is a term used to describe the tilting/movement of a ship at sea.  Given pitching is also a brewing term, it seemed like a good fit.

# Metrics

## Prometheus

For each Tilt the followed Prometheus metrics are created:

```
# HELP beacons_received_total Number of beacons received
# TYPE beacons_received_total counter
beacons_received_total{color="Purple"} 1.0

# HELP temperature_fahrenheit Temperature in fahrenheit
# TYPE temperature_fahrenheit gauge
temperature_fahrenheit{color="Purple"} 69.0

# HELP temperature_celcius Temperature in celcius
# TYPE temperature_celcius gauge
temperature_celcius{color="Purple"} 21.0

# HELP gravity Gravity of the beer
# TYPE gravity gauge
gravity{color="Purple"} 1.035
```

