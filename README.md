# Rhasspy Home Assistant Hermes

[![Continous Integration](https://github.com/rhasspy/rhasspy-homeassistant-hermes/workflows/Tests/badge.svg)](https://github.com/rhasspy/rhasspy-homeassistant-hermes/actions)
[![GitHub license](https://img.shields.io/github/license/rhasspy/rhasspy-homeassistant-hermes.svg)](https://github.com/rhasspy/rhasspy-homeassistant-hermes/blob/master/LICENSE)

Handles intents using [Home Assistant](https://www.home-assistant.io/) and [Hass.io](https://www.home-assistant.io/hassio/)

## Running With Docker

```bash
docker run -it rhasspy/rhasspy-homeassistant-hermes:<VERSION> <ARGS>
```

## Building From Source

Clone the repository and create the virtual environment:

```bash
git clone https://github.com/rhasspy/rhasspy-homeassistant-hermes.git
cd rhasspy-homeassistant-hermes
make venv
```

Run the `bin/rhasspy-homeassistant-hermes` script to access the command-line interface:

```bash
bin/rhasspy-homeassistant-hermes --help
```

## Building the Debian Package

Follow the instructions to build from source, then run:

```bash
source .venv/bin/activate
make debian
```

If successful, you'll find a `.deb` file in the `dist` directory that can be installed with `apt`.

## Building the Docker Image

Follow the instructions to build from source, then run:

```bash
source .venv/bin/activate
make docker
```

This will create a Docker image tagged `rhasspy/rhasspy-homeassistant-hermes:<VERSION>` where `VERSION` comes from the file of the same name in the source root directory.

NOTE: If you add things to the Docker image, make sure to whitelist them in `.dockerignore`.

## Command-Line Options

```
usage: rhasspy-homeassistant-hermes [-h] --url URL
                                    [--access-token ACCESS_TOKEN]
                                    [--api-password API_PASSWORD]
                                    [--handle-type {event,intent}]
                                    [--event-type-format EVENT_TYPE_FORMAT]
                                    [--pem-file PEM_FILE] [--host HOST]
                                    [--port PORT] [--siteId SITEID] [--debug]

optional arguments:
  -h, --help            show this help message and exit
  --url URL             URL of Home Assistant server
  --access-token ACCESS_TOKEN
                        Long-lived access token (Authorization)
  --api-password API_PASSWORD
                        API password (X-HA-Access, deprecated)
  --handle-type {event,intent}
                        Use Home Assistant events or intent API
  --event-type-format EVENT_TYPE_FORMAT
                        Format string for event types
  --pem-file PEM_FILE   Path to PEM file for self-signed certificates
  --host HOST           MQTT host (default: localhost)
  --port PORT           MQTT port (default: 1883)
  --siteId SITEID       Hermes siteId(s) to listen for (default: all)
  --debug               Print DEBUG messages to the console
```
