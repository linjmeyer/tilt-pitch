# Pitch (Tilt Hydrometer tool)

Pitch is an unofficial replacement for Tilt Hydrometer mobile apps and TiltPi software.  Tilt hardware is required.  It is designed to be easy to use and integrated with other tools like Promethues and InfluxDB for metrics, or any generic third party source using webhooks.

# Why

The Tilt hardware is impressive, but the mobile apps and TiltPi are confusing and buggy.  This project aims to provide a better more reliable solution, but is focused on more tech-savvy brewers than the official Tilt projects.  

# Features

The following features are implemented, planned, or will be investigated in the future:

* [x] Track multiple Tilts at once
* [x] Prometheus Metrics
* [x] Tilt status log file (JSON)
* [X] InfluxDB Metrics
* [X] Multiple logging and metric sources simultaneously
* [X] Webhooks for supporting generic integrations (similar to Tilt's Cloud Logging feature)
* [X] Gravity, original gravity, ABV, temperature and apparent attenuation
* [X] Custom Beer/brew names (e.g. purple tilt = Pumpkin Ale)
* [ ] Brewing Cloud Services (Brewstats, Brewer's Friend, etc.)
* [ ] Google Sheets (using any Google Drive)

# Installation

Pitch will only work on Linux, with libbluetooth-dev installed.  [See examples/install/prereq.sh](https://github.com/linjmeyer/tilt-pitch/blob/master/examples/install/prereqs.sh) for 
an example of how to do this using apt-get (Ubuntu, Raspberry Pi, etc).  

After setting up prereqs install using: `pip3 install tilt-pitch`
Pitch can be run using: `python3 -m pitch`

## Configuration

Custom configurations can be used by creating a file `pitch.json` in the working directory you are running Pitch from.

| Option                       | Purpose                      | Default               |
| ---------------------------- | ---------------------------- | --------------------- |
| `simulate_beacons` (bool) | Creates fake Tilt beacon events instead of scanning, useful for testing | False |
| `webhook_urls` (array) | Adds webhook URLs for Tilt status updates | None/empty |
| `log_file_path` (str) | Path to file for JSON event logging | `pitch_log.json` |
| `log_file_max_mb` (int) | Max JSON log file size in megabytes | `10` |
| `prometheus_enabled` (bool) | Enable/Disable Prometheus metrics | `true` |
| `prometheus_port` (int) | Port number for Prometheus Metrics | `8000` |
| `influxdb_hostname` (str) | Hostname for InfluxDB database | None/empty |
| `influxdb_port` (int) | Port for InfluxDB database | None/empty |
| `influxdb_database` (str) | Name of InfluxDB database | None/empty |
| `influxdb_username` (str) | Username for InfluxDB | None/empty |
| `influxdb_batch_size` (int) | Number of events to batch | `10` |
| `influxdb_timeout_seconds` (int) | Timeout of InfluxDB reads/writes | `5` |
| `brewfather_custom_stream_url` (str) | URL of Brewfather Custom Stream | None/empty |
| `{color}_name` (str) | Name of your brew, where {color} is the color of the Tilt (purple, red, etc) | Color (e.g. purple, red, etc) |
| `{color}_original_gravity` (float) | Original gravity of the beer, where {color} is the color of the Tilt (purple, red, etc) | None/empty |

## Running without a Tilt or on Mac/Windows

If you want to run Tilt on a non-linux system, for development, or without a Tilt you can use the `--simulate-beacons` flag to create fake
beacon events instead of scanning for Tilt events via Bluetooth.  

`python3 -m pitch --simulate-beacons`

# Integrations

* [Prometheus](#Prometheus-Metrics)
* [InfluxDb](#InfluxDB-Metrics)
* [Webhook](#Webhook)
* [JSON Log File](#JSON-Log-File)
* [Brewfather](#Brewfather)

Don't see one you want, send a PR implementing [CloudProviderBase](https://github.com/linjmeyer/tilt-pitch/blob/master/pitch/abstractions/cloud_provider.py)

## Prometheus Metrics

Prometheus metrics are hosted on port 8000.  For each Tilt the followed Prometheus metrics are created:

```
# HELP pitch_beacons_received_total Number of beacons received
# TYPE pitch_beacons_received_total counter
pitch_beacons_received_total{name="Pumpkin Ale", color="purple"} 3321.0

# HELP pitch_temperature_fahrenheit Temperature in fahrenheit
# TYPE pitch_temperature_fahrenheit gauge
pitch_temperature_fahrenheit{name="Pumpkin Ale", color="purple"} 69.0

# HELP pitch_temperature_celcius Temperature in celcius
# TYPE pitch_temperature_celcius gauge
pitch_temperature_celcius{name="Pumpkin Ale", color="purple"} 21.0

# HELP pitch_gravity Gravity of the beer
# TYPE pitch_gravity gauge
pitch_gravity{name="Pumpkin Ale", color="purple"} 1.035

# HELP pitch_alcohol_by_volume ABV of the beer
# TYPE pitch_alcohol_by_volume gauge
pitch_alcohol_by_volume{name="Pumpkin Ale", color="purple"} 5.63

# HELP pitch_apparent_attenuation Apparent attenuation of the beer
# TYPE pitch_apparent_attenuation gauge
pitch_apparent_attenuation{name="Pumpkin Ale", color="purple"} 32.32
```

## Webhook

Unlimited webhooks can be configured using the config option `webhook_urls`.  Each Tilt status broadcast will result in a webhook call to all URLs.

Webhooks are sent as HTTP POST with the following json payload:

```
{
    "name": "Pumpkin Ale",
    "color": "purple",
    "temp_fahrenheit": 69,
    "temp_celsius": 21,
    "gravity": 1.035,
    "alcohol_by_volume": 5.63,
    "apparent_attenuation": 32.32
}
```

## JSON Log File

Tilt status broadcast events can be logged to a json file using the config option `log_file_path`.  Each event is a newline.  Example file:

```
{"timestamp": "2020-09-11T02:15:30.525232", "name": "Pumpkin Ale", "color": "purple", "temp_fahrenheit": 70, "temp_celsius": 21, "gravity": 0.997, "alcohol_by_volume": 5.63, "apparent_attenuation": 32.32}
{"timestamp": "2020-09-11T02:15:32.539619", "name": "Pumpkin Ale", "color": "purple", "temp_fahrenheit": 70, "temp_celsius": 21, "gravity": 0.997, "alcohol_by_volume": 5.63, "apparent_attenuation": 32.32}
{"timestamp": "2020-09-11T02:15:33.545388", "name": "Pumpkin Ale", "color": "purple", "temp_fahrenheit": 70, "temp_celsius": 21, "gravity": 0.997, "alcohol_by_volume": 5.63, "apparent_attenuation": 32.32}
{"timestamp": "2020-09-11T02:15:34.548556", "name": "Pumpkin Ale", "color": "purple", "temp_fahrenheit": 70, "temp_celsius": 21, "gravity": 0.997, "alcohol_by_volume": 5.63, "apparent_attenuation": 32.32}
{"timestamp": "2020-09-11T02:15:35.557411", "name": "Pumpkin Ale", "color": "purple", "temp_fahrenheit": 70, "temp_celsius": 21, "gravity": 0.997, "alcohol_by_volume": 5.63, "apparent_attenuation": 32.32}
{"timestamp": "2020-09-11T02:15:36.562158", "name": "Pumpkin Ale", "color": "purple", "temp_fahrenheit": 70, "temp_celsius": 21, "gravity": 0.996, "alcohol_by_volume": 5.63, "apparent_attenuation": 32.32}
```

## InfluxDB Metrics

Metrics can be sent to an InfluxDB database.  See [Configuration section](#Configuration) for setting this up.  Pitch does not create the database
so it must be created before using Pitch.  

Each beacon event from a Tilt will create a measurement like this:

```json
{
    "measurement": "tilt",
    "tags": {
        "name": "Pumpkin Ale", 
        "color": "purple"
    },
    "fields": {
        "temp_fahrenheit": 70,
        "temp_celsius": 21,
        "gravity": 1.035,
        "alcohol_by_volume": 5.63,
        "apparent_attenuation": 32.32
    }
}
```  

and can be queried with something like:

```sql
SELECT mean("gravity") AS "mean_gravity" FROM "pitch"."autogen"."tilt" WHERE time > :dashboardTime: AND time < :upperDashboardTime: AND "name"='Pumpkin Ale' GROUP BY time(:interval:) FILL(previous)
```

## Brewfather

Tilt data can be logged to Brewfather using their Custom Log Stream feature.  See [Configuration section](#Configuration) for setting this up in the Pitch config.  Brewfather
only allows logging data every fifteen minutes (per Tilt).  Devices will show as `PitchTilt{color}`.

To setup login into Brewfather > Settings > PowerUps > Enable Custom Stream > Copy the URL into your Pitch config

![Configuring Brewfather Custom Stream URL](misc/brewfather_custom_stream.png)

# Examples

See the examples directory for:

* InfluxDB Grafana Dashboard
* Running Pitch as a systemd service
* pitch.json configuration file

# Other

## Buy me a coffee (beer)

![Buy me a coffee (beer)](misc/buy-me-a-coffee.png)

If you like Pitch, feel free to coffee (or a beer) here: https://www.buymeacoffee.com/linjmeyer

## Name

It's an unofficial tradition to name tech projects using nautical terms.  Pitch is a term used to describe the tilting/movement of a ship at sea.  Given pitching is also a brewing term, it seemed like a good fit.
